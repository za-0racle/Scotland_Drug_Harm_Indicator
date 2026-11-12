import csv
import json
import pytest
from openpyxl import load_workbook
from analysis.phase9_emerging_substances.extract import ROOT,SOURCES,extract,sha,count,definition
from analysis.phase9_emerging_substances.analyse import summarise,definitions,editions

@pytest.fixture(scope='module')
def extracted():
    rows=[];totals=[]
    for filename,(vintage,pub,sheets) in SOURCES.items():
        data,total,metadata=extract(ROOT/'datasets/Group3_Item2_Data'/filename,vintage,pub,sheets)
        assert len(metadata)==len(sheets)
        rows.extend(data);totals.extend(total)
    return rows,totals

def test_all_source_cells_and_labels(extracted):
    rows,totals=extracted
    for filename in SOURCES:
        path=ROOT/'datasets/Group3_Item2_Data'/filename
        workbook=load_workbook(path,data_only=True)
        digest=sha(path)
        for row in rows+totals:
            if row['source_workbook']!=path.relative_to(ROOT).as_posix():continue
            sheet=workbook[row['sheet']]
            assert sheet[row['source_cell']].value==row['count']
            assert sheet[row['label_cell']].value==row['substance_label']
            assert sheet[row['year_cell']].value==row['year_header_raw']
            assert int(str(sheet[row['year_cell']].value)[:4])==row['year']
            assert row['source_sha256']==digest
        workbook.close()

@pytest.mark.parametrize('raw,expected',[(None,(None,'missing')),('[c]',(None,'suppressed')),('*',(None,'suppressed')),('[x]',(None,'unavailable')),('text',(None,'non_numeric')),(0,(0,'observed')),('12',(12,'observed'))])
def test_quality(raw,expected):assert count(raw)==expected

@pytest.mark.parametrize('raw',[-1,1.2,float('nan'),True])
def test_invalid_counts(raw):
    with pytest.raises(ValueError):count(raw)

def test_definitions_and_totals(extracted):
    rows,totals=extracted
    assert definition('SUB1a',2007)!=definition('SUB1a',2008)
    assert definition('SUB1a',2024)!=definition('SUB2a',2024)
    assert definition('SUB1a',2024)!=definition('SUB1b',2024)
    assert all(not r['substance_label'].startswith('Total number of ') for r in rows)
    assert all(r['label_class']=='published_total' for r in totals)
    assert len({(r['vintage'],r['sheet'],r['substance_label'],r['year']) for r in rows})==len(rows)

def test_changes_and_order(extracted):
    inventory,changes=summarise(list(reversed(extracted[0])))
    brom=[r for r in changes if r['vintage']=='2024' and r['sheet']=='SUB1a' and r['substance_label']=='BROMAZOLAM']
    assert [r['year'] for r in brom]==list(range(2000,2025))
    assert next(r for r in brom if r['year']==2008)['annual_change'] is None
    assert next(r for r in brom if r['year']==2022)['annual_change_pct'] is None
    assert brom[-1]['annual_change']==-80
    summary=next(r for r in inventory if r['vintage']=='2024' and r['sheet']=='SUB1a' and r['substance_label']=='BROMAZOLAM' and r['first_reporting_year']==2008)
    assert summary['first_positive_year']==2022
    assert not summary['intermittent_recorded_involvement']

def test_absent_label_and_vintages(extracted):
    rows=extracted[0]
    item=next(r for r in definitions(rows) if r['substance_label']=='ISOTONITAZENE' and r['year']==2024)
    assert item['SUB1b'] is None and item['SUB1b_cell'] is None
    assert item['SUB1a']==0
    paired=editions(rows)
    assert paired and all(r['year']<=2023 for r in paired)

def test_intermittence_requires_return_and_missing_breaks_changes(extracted):
    base=next(r for r in extracted[0] if r['vintage']=='2024' and r['sheet']=='SUB1a' and r['year']==2008)
    def sample(values):return [dict(base,year=2008+i,count=value) for i,value in enumerate(values)]
    assert not summarise(sample([0,2,0]))[0][0]['intermittent_recorded_involvement']
    assert summarise(sample([2,0,2]))[0][0]['intermittent_recorded_involvement']
    summaries,changes=summarise(sample([2,None,4]))
    assert not summaries[0]['intermittent_recorded_involvement']
    assert changes[-1]['annual_change'] is None

def test_reproducibility_and_preservation(tmp_path):
    from analysis.phase9_emerging_substances.run import run,protected
    before=protected()
    first=tmp_path/'first';second=tmp_path/'second'
    run(first);run(second)
    for path in first.rglob('*'):
        if path.is_file() and path.name!='run_manifest.json':
            assert sha(path)==sha(second/path.relative_to(first)),path.name
    manifest=json.loads((first/'run_manifest.json').read_text())
    assert len(manifest['input_hashes'])==3
    assert len(manifest['figure_hashes'])==10
    with (first/'observations.csv').open(encoding='utf-8',newline='') as handle:
        assert len(list(csv.DictReader(handle)))>40000
    assert protected()==before
    with pytest.raises(FileExistsError):run(first)
