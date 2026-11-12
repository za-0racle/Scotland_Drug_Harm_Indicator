"""Descriptive summaries separated by edition, sheet and definition regime."""
from collections import defaultdict

SELECTED=('BROMAZOLAM','METONITAZENE','PROTONITAZENE','XYLAZINE','ETIZOLAM','DIAZEPAM','ISOTONITAZENE')

def summarise(rows):
    groups=defaultdict(list)
    for row in rows:groups[(row['vintage'],row['sheet'],row['substance_label'],row['reporting_definition'])].append(row)
    summaries=[];changes=[]
    for key,values in sorted(groups.items()):
        values=sorted(values,key=lambda r:r['year']);observed=[r for r in values if r['count'] is not None];positive=[r for r in observed if r['count']>0]
        complete=len(observed)==len(values);peak=max((r['count'] for r in observed),default=None)
        run=0;previous=None;deltas=[]
        for row in values:
            delta=row['count']-previous['count'] if previous and row['year']==previous['year']+1 and row['count'] is not None and previous['count'] is not None else None
            pct=delta/previous['count']*100 if delta is not None and previous['count']>0 else None
            changes.append(dict(row,annual_change=delta,annual_change_pct=pct,change_status='no_comparable_prior_year_in_same_definition' if delta is None else 'previous_zero_percentage_undefined' if previous['count']==0 else 'comparable'))
            deltas.append(delta);previous=row
        for delta in reversed(deltas):
            if delta is not None and delta>0:run+=1
            else:break
        latest_delta=deltas[-1];direction='insufficient_evidence' if latest_delta is None else 'increasing_recorded_involvement' if latest_delta>0 else 'declining_recorded_involvement' if latest_delta<0 else 'unchanged_recorded_count'
        first=positive[0] if positive else None;last=positive[-1] if positive else None
        prior=[r for r in values if first and r['year']<first['year']]
        zero_before=len(prior) if first and all(r['count']==0 for r in prior) else None
        intermittent=bool(complete and first and last and any(r['count']==0 for r in values if first['year']<r['year']<last['year']))
        summaries.append(dict(vintage=key[0],sheet=key[1],substance_label=key[2],reporting_definition=key[3],endpoint=values[0]['endpoint'],publication_date=values[0]['publication_date'],first_reporting_year=values[0]['year'],last_reporting_year=values[-1]['year'],first_positive_year=first['year'] if first else None,last_positive_year=last['year'] if last else None,first_positive_cell=first['source_cell'] if first else None,positive_at_left_boundary=bool(first and first['year']==values[0]['year']),published_zero_years=[r['year'] for r in observed if r['count']==0],missing_or_suppressed_years=[r['year'] for r in values if r['count'] is None],peak_count=peak,peak_years=[r['year'] for r in observed if r['count']==peak],latest_count=values[-1]['count'],latest_change=latest_delta,latest_direction=direction,consecutive_latest_increases=run,preceding_published_zero_years=zero_before,newly_recorded_in_available_segment=bool(first and prior and zero_before==len(prior)),intermittent_recorded_involvement=intermittent,source_workbook=values[0]['source_workbook'],source_sha256=values[0]['source_sha256'],source_cells=[r['source_cell'] for r in values],interpretation='Recorded involvement only; zero is not absence; no population rate or discovery/causality claim'))
    return summaries,sorted(changes,key=lambda r:(r['vintage'],r['sheet'],r['substance_label'],r['year']))

def editions(rows):
    index={(r['vintage'],r['sheet'],r['substance_label'],r['year']):r for r in rows};paired=[]
    for row in rows:
        if row['vintage']!='2023':continue
        later=index.get(('2024',row['sheet'],row['substance_label'],row['year']))
        if later:
            paired.append(dict(sheet=row['sheet'],substance_label=row['substance_label'],year=row['year'],earlier_count=row['count'],later_count=later['count'],difference=later['count']-row['count'] if later['count'] is not None and row['count'] is not None else None,earlier_workbook=row['source_workbook'],earlier_cell=row['source_cell'],later_workbook=later['source_workbook'],later_cell=later['source_cell']))
    return paired

def definitions(rows):
    index={(r['sheet'],r['substance_label'],r['year']):r for r in rows if r['vintage']=='2024'};result=[]
    for label in SELECTED:
        for year in range(2008,2025):
            record=dict(substance_label=label,year=year,publication_date='2025-09-02',interpretation='Separate reported endpoints; no summation or independence assumption')
            for sheet in ('SUB1a','SUB1b','SUB2a','SUB2b'):
                source=index.get((sheet,label,year));record[sheet]=source['count'] if source else None;record[sheet+'_cell']=source['source_cell'] if source else None
            result.append(record)
    return result
