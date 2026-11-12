"""Isolated, reproducible Phase 9 extraction and descriptive analysis."""
import argparse
import csv
import json
import platform
from importlib.metadata import version
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from .extract import ROOT, SOURCES, extract, sha
from .analyse import SELECTED, summarise, editions, definitions
from .context import chronology, existing_context, NRS_URL
from .figures import figures

HERE=Path(__file__).resolve().parent

def protected():
    from analysis.phase6.run import preserve
    result=preserve()
    manifest=json.loads((ROOT/'analysis/phase6/outputs/run_manifest.json').read_text())
    for path,expected in {**manifest['input_hashes'],**manifest['code_hashes']}.items():
        if sha(ROOT/path)!=expected: raise ValueError('Protected input/code changed: '+path)
    for name,expected in manifest['output_hashes'].items():
        if sha(ROOT/'analysis/phase6/outputs'/name)!=expected: raise ValueError('Protected Phase 6 output changed: '+name)
    for path in (ROOT/'analysis/phase6').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts: result[path.relative_to(ROOT).as_posix()]=sha(path)
    return result

def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

def write_csv(path,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        writer.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)

def run(directory=None):
    before=protected();directory=Path(directory or HERE/'outputs').resolve()
    if directory!=HERE/'outputs' and not any(p.endswith('.local') for p in directory.parts):
        raise ValueError('Use the default output directory or an ignored .local scratch directory')
    figure_dir=HERE/'figures' if directory==HERE/'outputs' else directory/'figures'
    if (directory.exists() and any(directory.iterdir())) or (figure_dir.exists() and any(figure_dir.iterdir())):
        raise FileExistsError('Refusing to overwrite research outputs')
    rows=[];totals=[];metadata=[];inputs={}
    for filename,(vintage,published,sheets) in SOURCES.items():
        path=ROOT/'datasets/Group3_Item2_Data'/filename
        observations,source_totals,source_metadata=extract(path,vintage,published,sheets)
        rows.extend(observations);totals.extend(source_totals);metadata.extend(source_metadata)
        inputs[path.relative_to(ROOT).as_posix()]=sha(path)
    keys=[(r['vintage'],r['sheet'],r['substance_label'],r['year']) for r in rows]
    if len(keys)!=len(set(keys)): raise ValueError('Duplicate observation key')
    inventory,changes=summarise(rows);vintages=editions(rows)
    selected=[r for r in inventory if r['vintage']=='2024' and r['substance_label'] in SELECTED]
    context,old_summary,context_hashes=existing_context();events=chronology()
    mapping={'BROMAZOLAM':'Street Benzodiazepines','ETIZOLAM':'Street Benzodiazepines','DIAZEPAM':'Prescribable Benzodiazepines','METONITAZENE':'Opioids','PROTONITAZENE':'Opioids','ISOTONITAZENE':'Opioids','XYLAZINE':None}
    quality=dict(observations=len(rows),source_totals=len(totals),duplicate_keys=0,
        quality_states=dict(Counter(r['quality_status'] for r in rows)),
        sheet_vintage_rows=dict(Counter(r['vintage']+' '+r['sheet'] for r in rows)),
        shared_vintage_cells=len(vintages),changed_shared_cells=sum(r['difference'] not in (None,0) for r in vintages),
        earlier_labels_absent_later=sorted(set((r['sheet'],r['substance_label']) for r in rows if r['vintage']=='2023')-set((r['sheet'],r['substance_label']) for r in rows if r['vintage']=='2024')),
        limitations=['Published zero is not verified absence','Absent label remains unavailable, never zero','No synonym merging or additive substance totals','Definition regime split at 2008','Registration year is not availability or occurrence date'])
    findings=dict(selected_SUB1a=[r for r in selected if r['sheet']=='SUB1a' and r['reporting_definition']=='implicated_or_potentially_contributing'],
        comparison_scope='Scotland national registered deaths only; no Greenock attribution',
        original_cross_source_summary=old_summary,
        interpretation='Descriptive recorded involvement; no new anomaly model, external validation, warning lead time or causality claim',
        testing_caveats=dict(reference=NRS_URL,review_date='2026-11-10',bromazolam='Limited testing before 2023',nitazenes='Limited testing before 2023',xylazine='Routine testing began in 2024'),
        foi_status='Pending in admitted research records; no alert metrics')
    directory.mkdir(parents=True,exist_ok=True)
    for name,data in [('observations',rows),('source_totals',totals),('substance_inventory',inventory),('annual_changes',changes),('definition_comparisons',definitions(rows)),('vintage_comparisons',vintages)]:
        write_csv(directory/(name+'.csv'),data)
    for name,data in [('source_metadata',metadata),('selected_substance_results',selected),('quality_report',quality),('findings',findings),('communication_chronology',sorted(events,key=lambda e:e['date'])),('broad_category_context',dict(mapping=mapping,records=context,limitation='Category mapping is contextual, not a chemical detection or matched cohort'))]:
        write_json(directory/(name+'.json'),data)
    figures(rows,changes,events,figure_dir)
    after=protected()
    if before!=after: raise ValueError('Protected earlier artifacts changed')
    for path,expected in inputs.items():
        if sha(ROOT/path)!=expected: raise ValueError('Source workbook changed')
    manifest=dict(version='phase9-1.0.0',executed_at_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        packages={name:version(name) for name in ('matplotlib','numpy','openpyxl','pillow')},
        input_hashes=inputs,context_hashes=context_hashes,protected_hashes=before,
        code_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in HERE.glob('*.py')},
        supporting_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE/'README.md',HERE/'requirements.txt',*sorted((HERE/'tests').glob('*.py'))]},
        output_hashes={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file()},
        figure_hashes={p.name:sha(p) for p in sorted(figure_dir.iterdir()) if p.is_file()})
    write_json(directory/'run_manifest.json',manifest)
    return quality

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path)
    print(json.dumps(run(parser.parse_args().output_dir),indent=2))
