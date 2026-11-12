import hashlib
import re
from collections import Counter
from functools import cached_property
from backend.schemas import Envelope,Filters
from backend.repositories.artifacts import ArtifactRepository,ArtifactError,CATALOG
from backend.repositories.supabase import SupabaseRepository,DatabaseError

BASE=['mortality_trends','forensic','assist','treatment','naloxone','annual']


class QueryError(Exception):pass


def geography(name,boundary=None):
    if name in ('Scotland','Scotland national total'):name='Scotland';boundary='country'
    elif name in ('NHS Greater Glasgow & Clyde','NHS Greater Glasgow and Clyde'):name='NHS Greater Glasgow and Clyde';boundary='health_board'
    elif not boundary:
        boundary='health_board' if name.startswith('NHS ') else 'police_division' if ': ' in name else 'national_testing_sample' if name=='Scotland forensic testing sample' else 'study_sample' if name.startswith('ASSIST') else 'unknown'
    return dict(geography_id=boundary+'-'+hashlib.sha256(name.encode()).hexdigest()[:12],name=name,boundary_type=boundary)


class PlatformService:
    def __init__(self,artifacts=None,database=None):self.artifacts=artifacts or ArtifactRepository();self.database=database or SupabaseRepository()

    @cached_property
    def registry(self):
        found={}
        for resource in BASE:
            rows,_=self.artifacts.load(resource)
            for row in rows:
                g=geography(row['geography'],row.get('boundary_type'));gid=g['geography_id']
                found.setdefault(gid,dict(g,resources=set(),indicators=set(),available=True))
                found[gid]['resources'].add(resource);found[gid]['indicators'].add(row['indicator_id'])
        greenock=geography('Greenock','locality')
        found[greenock['geography_id']]=dict(greenock,resources=set(),indicators=set(),available=False,limitation='No compatible Greenock-specific series; wider-area outcomes cannot be attributed to this locality')
        return {k:{**v,'resources':sorted(v['resources']),'indicators':sorted(v['indicators'])} for k,v in sorted(found.items())}

    def area(self,gid):
        if gid not in self.registry:raise QueryError('Unknown geographic identifier')
        return self.registry[gid]

    def decorate(self,row):
        result=dict(row)
        if result.get('geography'):
            result.update(geography(result['geography'],result.get('boundary_type')))
            result['source_geography']=row['geography']
        return result

    def query(self,resource,filters=Filters()):
        rows,meta=self.artifacts.load(resource)
        if resource=='diagnostics':
            index={(r['observation_id'],r['method']):r for r in self.artifacts.load('enhanced')[0]}
            rows=[dict(index[(r['observation_id'],r['method'])],**r) for r in rows]
        rows=[self.decorate(r) for r in rows]
        if resource=='evidence':
            candidates={r['comparison_id']:r for r in self.artifacts.load('candidates')[0]}
            rows=[dict(r,compatibility=candidates[r['comparison_id']],
                       period=candidates[r['comparison_id']]['left_period'],
                       related_geography_ids=[geography(candidates[r['comparison_id']][side+'_geography'])['geography_id'] for side in ('left','right')]) for r in rows]
        if filters.geography_id:
            area=self.area(filters.geography_id)
            if filters.boundary_type and area['boundary_type']!=filters.boundary_type:raise QueryError('Geography does not match requested boundary type')
            rows=[r for r in rows if r.get('geography_id')==filters.geography_id or filters.geography_id in r.get('related_geography_ids',[])]
        if filters.boundary_type:
            rows=[r for r in rows if r.get('boundary_type')==filters.boundary_type or ('compatibility' in r and any(self.area(g)['boundary_type']==filters.boundary_type for g in r['related_geography_ids']))]
        if filters.indicator:rows=[r for r in rows if r.get('indicator_id')==filters.indicator]
        if filters.category:rows=[r for r in rows if (r.get('substance_category') or str(r.get('indicator_id','')).partition(':')[2])==filters.category]
        if filters.model:rows=[r for r in rows if r.get('method',r.get('model'))==filters.model]
        if filters.start_year or filters.end_year or filters.start_date or filters.end_date:
            def matches(r):
                text=str(r.get('period_start') or r.get('year') or r.get('period') or r.get('target_period') or r.get('start') or '')
                match=re.match(r'^(\d{4})',text)
                if not match:return False
                year=int(match[1])
                if filters.start_year and year<filters.start_year:return False
                if filters.end_year and year>filters.end_year:return False
                if filters.start_date or filters.end_date:
                    start=r.get('period_start');end=r.get('period_end')
                    if not start or not end:return False # Never infer exact ASSIST dates.
                    if filters.start_date and end<filters.start_date.isoformat():return False
                    if filters.end_date and start>filters.end_date.isoformat():return False
                return True
            rows=[r for r in rows if matches(r)]
        if resource=='anomalies' and filters.signals_only:
            rows=[r for r in rows if r.get('classification')=='statistically_unusual_observation']
        if resource=='enhanced' and filters.signals_only:rows=[r for r in rows if r.get('signal') is True]
        if resource in ('anomalies','enhanced'):
            rows.sort(key=lambda r:(
                str(r.get('period_start') or r.get('period') or r.get('year') or ''),
                str(r.get('geography') or ''),
                str(r.get('indicator_id') or ''),
                str(r.get('method') or ''),
                str(r.get('window') or ''),
            ))
        total=len(rows);page=rows[filters.offset:filters.offset+filters.limit]
        return Envelope(state='ready' if total else 'empty',kind='research_result',data=page,total=total,offset=filters.offset,limit=filters.limit,metadata=meta,
                        message='' if total else 'No matching accessible research records; this is not evidence of no harm or no official alerts')

    def db(self,table,filters):
        rows=self.database.read(table)
        if table=='indicator_results':
            labels={r.get('configuration_id'):r.get('configuration_label') for r in self.database.read('indicator_configurations')}
            rows=[dict(r,configuration_label=labels.get(r.get('configuration_id'))) for r in rows]
        if table=='mortality_quarterly':
            rows=[dict(r,geography='Scotland',boundary_type='country',indicator_id='police_suspected_deaths',unit='count',period=f"{r['year']} Q{r['quarter']}",period_basis='legacy_calendar_quarter') for r in rows]
            if filters.geography_id and self.area(filters.geography_id)['name']!='Scotland':raise QueryError('Database mortality endpoint is national only; use geographic research endpoints for divisions')
            if filters.boundary_type and filters.boundary_type!='country':raise QueryError('Database mortality boundary is country')
            rows=[r for r in rows if (not filters.start_year or r['year']>=filters.start_year) and (not filters.end_year or r['year']<=filters.end_year)]
        return Envelope(state='ready' if rows else 'empty',kind='database_observation',data=rows[filters.offset:filters.offset+filters.limit],total=len(rows),offset=filters.offset,limit=filters.limit,
                        metadata=dict(table=table,storage='Supabase REST via server-side anon credential',analytical_version=None,limitations=['Existing RLS preserved; empty access does not establish no observations','Only reviewed mortality/configuration/result tables queried']),
                        message='' if rows else 'No accessible rows: table may be empty or RLS may withhold rows; not a successful data load')

    def overview(self):
        summary=self.artifacts.load('summary')[0][0]
        try:database=self.db('mortality_quarterly',Filters(limit=1000)).model_dump()
        except DatabaseError as error:database=dict(state='error',message=str(error),data=[],total=0)
        coverage=Counter(g['boundary_type'] for g in self.registry.values() if g['available'])
        latest=[]
        for resource in BASE:
            rows,meta=self.artifacts.load(resource)
            dates=sorted({str(r.get('source_data_cutoff') or r.get('period_end') or r.get('period') or '') for r in rows})
            latest.append(dict(resource=resource,records=len(rows),cutoff=dates[-1] if dates else None,provenance=meta))
        return Envelope(state='ready',kind='metadata',data=[dict(database=database,coverage=dict(coverage),sources=latest,
                        original_flags=summary['original_primary_flags'],original_runs=summary['original_runs'],cross_source_candidates=summary['cross_source_candidates'],
                        compatible_pairs=summary['compatibility']['compatible_contextual_evidence'],joint_signal_status='No established joint directional contextual signal',
                        research_status='Historical research prototype; no PHS endorsement or operational validation')],total=1)

    def geography_data(self,gid,section,filters):
        area=self.area(gid);filters=filters.model_copy(update={'geography_id':gid})
        if not area['available']:return Envelope(state='unavailable',kind='unavailable_evidence',message=area['limitation'],metadata=area)
        if section=='indicators':
            items=[]
            for resource in area['resources']:
                rows=self.query(resource,filters.model_copy(update={'limit':1000,'signals_only':False})).data
                for indicator in sorted({r['indicator_id'] for r in rows}):
                    values=[r for r in rows if r['indicator_id']==indicator]
                    items.append(dict(indicator_id=indicator,resource=resource,categories=sorted({r.get('substance_category') or r['indicator_id'].partition(':')[2] for r in values if r.get('substance_category') or ':' in r['indicator_id']}),unit=values[0].get('unit'),period_basis=values[0].get('period_basis')))
            return Envelope(state='ready' if items else 'empty',kind='metadata',data=items,total=len(items),metadata=area)
        if section=='anomalies':return self.query('enhanced' if filters.model and filters.model!='phase5_robust' else 'anomalies',filters if filters.model!='phase5_robust' else filters.model_copy(update={'model':None}))
        if section=='evidence':return self.query('evidence',filters)
        if section=='comparisons':
            if not filters.compare_to:return Envelope(state='unavailable',kind='unavailable_evidence',message='Select a second area with the same boundary and indicator')
            other=self.area(filters.compare_to)
            if other['boundary_type']!=area['boundary_type']:raise QueryError('Comparison areas must have the same boundary type')
            if not filters.indicator:
                return Envelope(state='unavailable',kind='unavailable_evidence',message='Select one indicator before comparing areas')
            resource=next((r for r in area['resources'] if r in other['resources'] and any(x['indicator_id']==filters.indicator for x in self.artifacts.load(r)[0]) and filters.indicator in other['indicators']),None)
            if not resource:return Envelope(state='unavailable',kind='unavailable_evidence',message='No compatible indicator for these areas')
            # Fetch both complete bounded series, then paginate the combined representation.
            def complete(gid):
                rows=[];position=0
                while True:
                    result=self.query(resource,filters.model_copy(update={'geography_id':gid,'offset':position,'limit':1000}))
                    rows.extend(result.data);position+=len(result.data)
                    if position>=result.total or not result.data:return rows,result.metadata
            left,meta=complete(gid);right,_=complete(filters.compare_to)
            items=[dict(r,comparison_role='first_area') for r in left]+[dict(r,comparison_role='second_area') for r in right]
            items.sort(key=lambda r:(str(r.get('period_start') or r.get('year') or r.get('period')),r['comparison_role']))
            meta=dict(meta,comparison='Same dataset, indicator and boundary; counts are not population rates')
            return Envelope(state='ready' if items else 'empty',kind='research_result',data=items[filters.offset:filters.offset+filters.limit],total=len(items),offset=filters.offset,limit=filters.limit,metadata=meta)
        resource=next((r for r in area['resources'] if not filters.indicator or any(x['indicator_id']==filters.indicator for x in self.artifacts.load(r)[0])),None)
        return self.query(resource,filters) if resource else Envelope(state='unavailable',kind='unavailable_evidence',message='Indicator unavailable for selected scope')
