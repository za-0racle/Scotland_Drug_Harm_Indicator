"""Read-only source/API capture. Never overwrites earlier or current evidence."""
import csv
import hashlib
import json
import sys
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from backend.services.mortality_adapter import fingerprint
from backend.services.platform import PlatformService
from backend.schemas import Filters
from backend.main import create_app
from fastapi.testclient import TestClient


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


if __name__=='__main__':
    names=['forensic-baseline.json','preservation-before.json','openapi-before.json']
    if any((OUT/n).exists() for n in names):raise SystemExit('Evidence already exists; capture refused without overwriting.')
    baseline=ROOT/'docs/baselines/task08b'
    old=next(r for r in json.loads((baseline/'resource-contracts.json').read_text()) if r['resource']=='forensic')
    service=PlatformService(); result=service.query('forensic',Filters(limit=1000,signals_only=False)).model_dump()
    rows=result['data']
    artifact=ROOT/result['metadata']['source_path']
    original=next(r for r in json.loads((baseline/'file-inventory.json').read_text()) if r['path']==result['metadata']['source_path'])
    with artifact.open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f); strings=list(reader);fields=reader.fieldnames
    numeric_names={'observed_value','count','rate','lower95','upper95','total_deaths','prediction','forecast','statistic_value','lower_limit','upper_limit','suspected_deaths'}
    numerical=[{k:r[k] for k in sorted(r) if k in numeric_names or isinstance(r[k],(int,float)) and not isinstance(r[k],bool)} for r in rows]
    checks=dict(records=len(rows)==old['api_records']==210, response=fingerprint(rows)==old['ordered_response_fingerprint'],
                numerical=fingerprint(numerical)==old['numeric_field_projection_fingerprint'],metadata=result['metadata']==old['metadata'],
                artifact_sha=sha(artifact)==old['metadata']['artifact_sha256']==original['sha256'],
                csv_records=fingerprint(strings)==original['ordered_record_fingerprint'])
    source=ROOT/rows[0]['source_path']
    with source.open(encoding='utf-8',newline='') as f:raw=list(csv.DictReader(f))
    checks['source_sha']=sha(source)==rows[0]['source_sha256']
    checks['raw_measure']=all(r['measure']=='Number' and r['value'].isdigit() for r in raw)
    checks['categories']=len({r['drug_name'] for r in raw})==7
    checks['raw_slots']=len(raw)==210 and len({(r['Quarter'],r['drug_name']) for r in raw})==210
    if not all(checks.values()):raise SystemExit('Material Task 08B discrepancy; adapter implementation must stop: '+str(checks))
    manifests=[]
    for e in json.loads((baseline/'manifest-verification.json').read_text()):
        p=ROOT/Path(e['manifest']).parent/e['file']
        manifests.append(dict(path=p.relative_to(ROOT).as_posix(),expected=e['expected'],match=sha(p)==e['expected']))
    if not all(e['match'] for e in manifests):raise SystemExit('Manifest discrepancy; stop before implementation.')
    paths=[]
    for directory in ['datasets','analysis','backend','src','tests','e2e','supabase','g3-indicator','docs/baselines/task08b','docs/baselines/task08c','docs/baselines/task08d']:
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and not any(x in p.parts for x in ('.venv','__pycache__','test_scratch.local','.pytest_cache','node_modules')))
    paths.extend(ROOT.glob('group3*'))
    paths.extend(ROOT/p for p in ['package.json','package-lock.json','g3-indicator.zip','docs/TASK08C_MORTALITY_ADAPTER_REPORT.md','docs/TASK08D_FRONTEND_MIGRATION_REPORT.md'])
    protected={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths)) if p.is_file()}
    capture=dict(task08b_comparisons=checks,manifest_checks=manifests,response=result,raw_source_records=raw,
                 artifact_fields=fields,original_csv_record_fingerprint=original['ordered_record_fingerprint'],
                 ordered_response_fingerprint=old['ordered_response_fingerprint'],numeric_fingerprint=old['numeric_field_projection_fingerprint'],
                 source_sha256=sha(source),categories=sorted({r['drug_name'] for r in raw}),
                 observed_nulls=sum(r['observed_value'] is None for r in rows),observed_zeros=sum(r['observed_value']==0 for r in rows),
                 quarters=len({r['period'] for r in rows}),unit=sorted({r['unit'] for r in rows}),
                 original_measure=sorted({r['measure'] for r in raw}),publication_date_nulls=sum(r['publication_date'] is None for r in rows))
    client=TestClient(create_app())
    for name,value in [('forensic-baseline.json',capture),('preservation-before.json',protected),('openapi-before.json',client.get('/openapi.json').json())]:
        (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(task08b_checks=checks,records=len(rows),nulls=capture['observed_nulls'],zeros=capture['observed_zeros'],quarters=capture['quarters'],protected_files=len(protected),manifest_matches=sum(x['match'] for x in manifests))))
