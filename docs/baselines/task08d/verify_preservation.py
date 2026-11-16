"""Read-only verification against prior tasks; writes this new evidence directory."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


if __name__=='__main__':
    old=json.loads((ROOT/'docs/baselines/task08b/preservation-before.json').read_text(encoding='utf-8'))
    allowed={'backend/main.py','src/api/client.js','src/platform/geography-data.js'}
    changed=[p for p,h in old.items() if sha(ROOT/p)!=h]
    previous=json.loads((OUT/'previous-task-integrity.json').read_text(encoding='utf-8'))
    prior_changes=[p for p,h in previous.items() if sha(ROOT/p)!=h]
    checks=[]
    for record in json.loads((ROOT/'docs/baselines/task08b/manifest-verification.json').read_text(encoding='utf-8')):
        p=ROOT/Path(record['manifest']).parent/record['file']
        checks.append(dict(path=p.relative_to(ROOT).as_posix(),match=sha(p)==record['expected']))
    result=dict(task08b_original_files=len(old),unchanged_since_task08b=len(old)-len(changed),changed_since_task08b=changed,
                task08d_existing_application_changes=['src/api/client.js','src/platform/geography-data.js'],
                task08c_integration_unchanged=sha(ROOT/'backend/main.py')==previous['backend/main.py'],
                previous_task_files_checked=len(previous),previous_task_files_changed=prior_changes,
                manifest_matches=sum(c['match'] for c in checks),manifest_checks=checks,
                unexpected_changes=sorted(set(changed)-allowed),
                generated_files='Builds, screenshots, bytecode and test scratch are excluded; no research recalculation.')
    (OUT/'preservation-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='manifest_checks'}))
    if prior_changes or result['unexpected_changes'] or not all(c['match'] for c in checks):raise SystemExit(1)
