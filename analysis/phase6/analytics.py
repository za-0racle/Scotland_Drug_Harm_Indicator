"""Exact-year descriptive comparisons; no inferred local warning threshold."""
from collections import defaultdict
from analysis.phase6.data import INDICATOR,number


def change(value,reference):
    if value is None or reference is None:
        return None,None
    return value-reference,100*(value-reference)/reference if reference else None


def trends(rows):
    grouped=defaultdict(dict)
    for row in rows:
        if row['indicator_id']!=INDICATOR or row['period_basis']!='calendar_year_of_registration' or row['sex']!='Persons':
            raise ValueError('Only matched NRS registered Persons annual counts')
        year=row['year'];key=(row['geography'],row['boundary_type'],row['source_sha256'])
        if year in grouped[key]:
            raise ValueError('Duplicate geographic year')
        number(row['observed_value'],True)
        grouped[key][year]=row
    result=[]
    for key,indexed in sorted(grouped.items()):
        for year,row in sorted(indexed.items()):
            value=row['observed_value'];r=dict(row)
            previous=indexed.get(year-1,{}).get('observed_value')
            delta,pct=change(value,previous)
            r.update(previous_value=previous,annual_change=delta,annual_change_pct=pct,
                     direction='unavailable' if delta is None else 'increase' if delta>0 else 'decrease' if delta<0 else 'unchanged',
                     one_death_pct_of_previous=100/previous if previous else None,
                     interpretation='Descriptive exact-period count comparison, not risk change or an anomaly',
                     rolling_method='Trailing complete annual windows including labelled current year; no future years')
            for lag in (3,5,10):
                reference=indexed.get(year-lag,{}).get('observed_value')
                absolute,relative=change(value,reference)
                r.update({f'reference_{lag}y':reference,f'change_{lag}y':absolute,f'change_{lag}y_pct':relative})
            for window in (3,5):
                values=[indexed.get(y,{}).get('observed_value') for y in range(year-window+1,year+1)]
                r[f'rolling_{window}y_mean']=sum(values)/window if all(v is not None for v in values) else None
                r[f'rolling_{window}y_complete']=all(v is not None for v in values)
            r['change_since_2010'],r['change_since_2010_pct']=change(value,indexed.get(2010,{}).get('observed_value'))
            result.append(r)
    return result


def compatible(a,b):
    if any(a.get(k)!=b.get(k) for k in ('indicator_id','period_basis','year','sex','source_sha256')):
        raise ValueError('Incompatible definition, year, sex, period basis or source vintage')
    if a['indicator_id']!=INDICATOR or a['geography']!='Inverclyde' or a['boundary_type']!='council' or b['geography']!='Scotland' or b['boundary_type']!='country':
        raise ValueError('Expected exact Inverclyde council and NRS Scotland scopes')


def comparisons(rows):
    indexed={(r['geography'],r['year']):r for r in rows}
    if len(indexed)!=len(rows):
        raise ValueError('Duplicate comparison observation')
    output=[]
    for year in sorted({r['year'] for r in rows}):
        local,national=indexed.get(('Inverclyde',year)),indexed.get(('Scotland',year))
        if local is None or national is None:
            raise ValueError('Comparison requires matching years; no interpolation')
        compatible(local,national)
        x,y=local['observed_value'],national['observed_value']
        if x is not None and y is not None and x>y:
            raise ValueError('Council count exceeds national total')
        output.append(dict(year=year,indicator_id=INDICATOR,period_basis=local['period_basis'],
                           local_geography='Inverclyde',local_boundary='council',national_geography='Scotland',national_boundary='country',
                           inverclyde_deaths=x,scotland_deaths=y,local_annual_change_pct=local['annual_change_pct'],
                           scotland_annual_change_pct=national['annual_change_pct'],
                           direction_agreement='unavailable' if 'unavailable' in (local['direction'],national['direction']) else 'same' if local['direction']==national['direction'] else 'different',
                           inverclyde_share_of_scotland_pct=100*x/y if x is not None and y else None,
                           inverclyde_index_2010=100+local['change_since_2010_pct'] if local['change_since_2010_pct'] is not None else None,
                           scotland_index_2010=100+national['change_since_2010_pct'] if national['change_since_2010_pct'] is not None else None,
                           source_sha256=local['source_sha256'],source_cells=[local['source_cell'],national['source_cell']],
                           interpretation='Same registered definition/vintage; local share is not population risk. Scotland includes Inverclyde; no independent-sample test'))
    return output


def rate_comparisons(rates):
    indexed={(r['geography'],r['start_year'],r['end_year']):r for r in rates}
    output=[]
    for start in range(2010,2021):
        a,b=indexed[('Inverclyde',start,start+4)],indexed[('Scotland',start,start+4)]
        for field in ('indicator_id','period_basis','unit','standard_population','source_sha256'):
            if a[field]!=b[field]:
                raise ValueError('Incompatible published rate definitions')
        x,y=a['rate'],b['rate']
        output.append(dict(period_label=a['period_label'],period_start=a['period_start'],period_end=a['period_end'],
                           inverclyde_rate=x,inverclyde_lower95=a['lower95'],inverclyde_upper95=a['upper95'],
                           scotland_rate=y,scotland_lower95=b['lower95'],scotland_upper95=b['upper95'],
                           rate_difference=x-y if x is not None and y is not None else None,
                           descriptive_rate_ratio=x/y if x is not None and y else None,
                           unit=a['unit'],standard_population=a['standard_population'],
                           source_rows=[a['source_row'],b['source_row']],source_sha256=a['source_sha256'],
                           interpretation='Ratio of rounded NRS five-year ASRs, not annual crude risk or a significance test; areas nested, periods overlap'))
    return output


def extrema(rows):
    output={}
    for area in ('Inverclyde','Scotland'):
        observed=[r for r in rows if r['geography']==area and r['observed_value'] is not None]
        if not observed:
            output[area]=dict(status='unavailable');continue
        low=min(r['observed_value'] for r in observed);high=max(r['observed_value'] for r in observed)
        output[area]=dict(lowest_count=low,lowest_years=[r['year'] for r in observed if r['observed_value']==low],
                          highest_count=high,highest_years=[r['year'] for r in observed if r['observed_value']==high],
                          reference_scope='Full frozen 2010–2024 descriptive history, not a prospective baseline')
    return output
