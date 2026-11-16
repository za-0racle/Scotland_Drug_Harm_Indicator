"""Verify 08C against immutable 08B evidence; write only this new directory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/baselines/task08b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


if __name__ == '__main__':
    before = json.loads((BASE/'preservation-before.json').read_text(encoding='utf-8'))
    changed = [p for p, value in before.items() if sha(ROOT/p) != value]
    allowed = ['backend/main.py']
    baseline_before = json.loads((OUT/'task08b-preservation-before.json').read_text(encoding='utf-8'))
    baseline_after = {p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}
    manifest_checks = []
    for entry in json.loads((BASE/'manifest-verification.json').read_text(encoding='utf-8')):
        path = ROOT / Path(entry['manifest']).parent / entry['file']
        manifest_checks.append(dict(path=path.relative_to(ROOT).as_posix(), expected=entry['expected'],
                                    actual=sha(path), match=sha(path) == entry['expected']))
    new_application = []
    for directory in ('backend','src','analysis','datasets','supabase','tests','e2e','g3-indicator'):
        for p in (ROOT/directory).rglob('*'):
            if not p.is_file() or any(s in p.parts for s in ('.venv','__pycache__','test_scratch.local','.pytest_cache','node_modules')): continue
            relative = p.relative_to(ROOT).as_posix()
            if relative not in before: new_application.append(relative)
    result = dict(original_protected_files=len(before), original_files_unchanged=len(before)-len(changed),
                  changed_existing_files=changed, permitted_integration_changes=allowed,
                  unexpected_changes=sorted(set(changed)-set(allowed)),
                  new_application_files=sorted(new_application),
                  task08b_files=len(baseline_before), task08b_unchanged=baseline_before == baseline_after,
                  manifest_matches=sum(x['match'] for x in manifest_checks), manifest_checks=manifest_checks,
                  notes='main.py only adds the versioned router import/registration. No research file exception is permitted; generated outputs/scratch are excluded.')
    (OUT/'preservation-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'manifest_checks'}))
    if result['unexpected_changes'] or not result['task08b_unchanged'] or not all(x['match'] for x in manifest_checks):
        raise SystemExit(1)
