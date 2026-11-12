"""Geographic extraction/compatibility checks, with labelled synthetic fixtures."""
import copy
import csv
import json

import pytest
from openpyxl import load_workbook

from analysis.phase6.data import WORKBOOK,YEARS,INDICATOR,extract,parse_counts,parse_rates,number,crude_rate
from analysis.phase6.analytics import trends,comparisons,compatible,rate_comparisons
from analysis.phase6.run import run,preserve


def matrix(sheet):
    workbook=load_workbook(WORKBOOK,read_only=True,data_only=True)
    try:
        return [list(row) for row in workbook[sheet].values]
    finally:
        workbook.close()


def test_exact_workbook_years_values_cells_and_crosschecks():
    counts,rates,metadata=extract()
    local=[r for r in counts if r['geography']=='Inverclyde']
    assert [r['year'] for r in local]==YEARS
    assert [r['observed_value'] for r in local]==[17,20,13,10,17,16,20,23,24,33,33,16,29,26,25]
    assert [r['source_cell'] for r in local]==[f'T{i}' for i in range(6,21)]
    assert len(counts)==30 and len(rates)==22
    assert metadata['publication_date']=='2025-09-02'
    assert all(r['indicator_id']==INDICATOR for r in counts+rates)
    assert all(r['total_check']=='matches_five_C1_counts' for r in rates)
    assert next(r for r in counts if r['geography']=='Scotland' and r['year']==2024)['observed_value']==1017


def test_exact_geography_and_duplicate_or_missing_years_fail():
    rows=matrix('Table_C1')
    changed=copy.deepcopy(rows);changed[4][19]='NHS Greater Glasgow and Clyde'
    with pytest.raises(ValueError,match='Exact area'):
        parse_counts(changed)
    changed=copy.deepcopy(rows);changed[6][0]=2010
    with pytest.raises(ValueError,match='duplicate'):
        parse_counts(changed)
    changed=copy.deepcopy(rows);del changed[5]
    with pytest.raises(ValueError,match='Missing year'):
        parse_counts(changed)
    changed=copy.deepcopy(rows);changed[5][0]='2010'
    with pytest.raises(ValueError,match='year label'):
        parse_counts(changed)


def test_suppression_and_true_zero_are_not_confused():
    for token in (None,'','[x]','[l]','[c]',':','x'):
        assert number(token,True) is None
    assert number(0,True)==0
    for token in (True,-1,1.5,'unrecognised','nan'):
        with pytest.raises(ValueError):
            number(token,True)
    rows=matrix('Table_C1');rows[5][19]='[x]';rows[6][19]=0
    parsed=parse_counts(rows)
    assert parsed[0]['observed_value'] is None
    assert parsed[1]['observed_value']==0
    calculated=trends([dict(r,source_sha256='synthetic_mutated_table_fixture') for r in parsed])
    local=[r for r in calculated if r['geography']=='Inverclyde']
    assert local[1]['annual_change_pct'] is None
    assert local[2]['annual_change_pct'] is None  # Zero denominator stays undefined.
    assert local[2]['rolling_3y_mean'] is None


def test_trends_use_exact_trailing_periods_and_no_future():
    counts,_,_=extract()
    local=[r for r in counts if r['geography']=='Inverclyde']
    before=trends(local[:-1]);after=trends(local)
    assert after[:-1]==before
    last=after[-1]
    assert last['annual_change']==-1 and last['annual_change_pct']==pytest.approx(-100/26)
    assert last['rolling_3y_mean']==pytest.approx(80/3)
    assert last['rolling_5y_mean']==25.8
    assert last['change_since_2010_pct']==pytest.approx(100*8/17)
    assert last['change_5y']==-8
    with_gap=trends([r for r in local if r['year']!=2023])[-1]
    assert with_gap['previous_value'] is None and with_gap['rolling_3y_mean'] is None
    with pytest.raises(ValueError,match='Duplicate'):
        trends(local+[local[0]])


def test_suspected_deaths_and_incompatible_year_or_boundary_are_rejected():
    counts,_,_=extract();a=counts[0];b=next(r for r in counts if r['geography']=='Scotland' and r['year']==a['year'])
    compatible(a,b)
    for changed in (dict(b,indicator_id='police_suspected_deaths'),dict(b,year=2011),dict(b,sex='Males'),dict(b,source_sha256='other_vintage')):
        with pytest.raises(ValueError):
            compatible(a,changed)
    with pytest.raises(ValueError):
        compatible(dict(a,geography='Greenock',boundary_type='locality'),b)
    with pytest.raises(ValueError):
        comparisons(trends(counts)[1:])


def test_published_five_year_rates_and_count_totals_are_matched():
    counts,rates,_=extract();latest=rate_comparisons(rates)[-1]
    assert latest['inverclyde_rate']==35.6 and latest['scotland_rate']==22.5
    assert latest['descriptive_rate_ratio']==pytest.approx(35.6/22.5)
    assert latest['inverclyde_lower95']==29.3 and latest['inverclyde_upper95']==41.8
    raw=matrix('Table_C4')
    target=next(i for i,r in enumerate(raw) if r[0]=='Inverclyde' and r[1]=='2020 - 2024')
    raw[target][5]=130
    with pytest.raises(ValueError,match='disagrees'):
        parse_rates(raw,counts)
    raw=matrix('Table_C4');raw[target][3]=50
    with pytest.raises(ValueError,match='confidence'):
        parse_rates(raw,counts)


def test_future_population_adapter_requires_exact_boundary_year_sex_and_definition():
    count=extract()[0][0]
    # SYNTHETIC TEST denominator only; never output as a real population.
    population=dict(geography='Inverclyde',boundary_type='council',year=2010,sex='Persons',
                    population=100000,measure='mid_year_resident_population',verified_compatible=True)
    assert crude_rate(count,population)==17
    for changed in (dict(population,boundary_type='health_board'),dict(population,geography='Greenock'),
                    dict(population,year=2011),dict(population,sex='Females'),dict(population,verified_compatible=False),
                    dict(population,measure='NumberAssessed')):
        with pytest.raises(ValueError):
            crude_rate(count,changed)
    assert crude_rate(count,dict(population,population=0)) is None
    assert crude_rate(dict(count,observed_value=None),population) is None


def test_full_reproduction_population_exclusion_hierarchy_and_preservation(tmp_path):
    before=preserve();one,two=tmp_path/'first',tmp_path/'second'
    first=run(one);second=run(two)
    assert first==second
    for path in one.iterdir():
        if path.name!='run_manifest.json':
            assert path.read_bytes()==(two/path.name).read_bytes(),path.name
    assert preserve()==before
    quality=json.loads((one/'data_quality_report.json').read_text())
    assert quality['annual_quality_states']=={'observed':30}
    assert quality['five_year_total_matches']==22
    assert all(r['geographic_key']=='HB' and not r['compatible_inverclyde_council'] for r in quality['population_audit'])
    contract=json.loads((one/'dashboard_data_contract.json').read_text())
    assert contract['greenock']['state']=='no_compatible_local_series'
    assert len(contract['annual_count_series'])==30 and len(contract['published_five_year_rates'])==22
    assert contract['findings']['local_anomaly_feasibility']['status'].startswith('not_estimated')
    with (one/'annual_population_rates.csv').open() as handle:
        rates=list(csv.DictReader(handle))
    assert len(rates)==15 and all(r['rate_per_100000']=='' for r in rates)
