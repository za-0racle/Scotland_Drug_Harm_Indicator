"""Task 08B evidence capture: reads sources; writes only this baseline directory.

Run from repository root with the existing analysis Python and -B. No models run.
Fingerprints are comparisons of existing values, not scientific validation.
"""
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def preservation():
    paths = set()
    for folder in ('datasets', 'analysis', 'g3-indicator', 'src', 'backend', 'supabase', 'tests', 'e2e'):
        for p in (ROOT / folder).rglob('*'):
            if p.is_file() and not any(x in p.parts for x in ('.venv', '__pycache__', 'test_scratch.local', '.pytest_cache', 'node_modules')):
                paths.add(p)
    paths.update(ROOT.glob('group3*'))
    for name in ('package.json', 'package-lock.json', 'vite.config.js', 'playwright.config.js', 'playwright.overview.config.js', 'g3-indicator.zip'):
        paths.add(ROOT / name)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def capture():
    from backend.repositories.artifacts import ArtifactRepository, CATALOG
    from backend.services.platform import PlatformService
    from backend.schemas import Filters
    from backend.main import create_app
    from fastapi.testclient import TestClient

    save('preservation-before.json', preservation())
    files = []
    for relative, sha in preservation().items():
        p = ROOT / relative
        if p.suffix not in ('.csv', '.json') or not (relative.startswith(('datasets/', 'analysis/', 'g3-indicator/public/data/')) or p.name.startswith('group3')):
            continue
        item = dict(path=relative, sha256=sha, bytes=p.stat().st_size)
        try:
            if p.suffix == '.csv':
                with p.open(encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f); rows = list(reader); item['fields'] = reader.fieldnames
                item.update(records=len(rows), empty_by_field={k: sum(r.get(k) == '' for r in rows) for k in (reader.fieldnames or [])},
                            exact_duplicate_rows=len(rows)-len({digest(r) for r in rows}), ordered_record_fingerprint=digest(rows))
            else:
                obj = json.loads(p.read_text(encoding='utf-8-sig'))
                item.update(json_type=type(obj).__name__, entries=len(obj) if isinstance(obj, (dict, list)) else 1,
                            fields=sorted(set().union(*(r.keys() for r in obj if isinstance(r, dict)))) if isinstance(obj, list) else list(obj) if isinstance(obj, dict) else [])
            item['inspection'] = 'parsed'
        except (ValueError, UnicodeError) as error:
            item['inspection'] = type(error).__name__
        files.append(item)
    save('file-inventory.json', files)
    checks = []
    for p in sorted((ROOT / 'analysis').rglob('run_manifest.json')):
        if 'test_scratch.local' in p.parts: continue
        manifest = json.loads(p.read_text(encoding='utf-8-sig'))
        for name, expected in manifest.get('output_hashes', {}).items():
            q = p.parent / name
            actual = hashlib.sha256(q.read_bytes()).hexdigest() if q.exists() else None
            checks.append(dict(manifest=p.relative_to(ROOT).as_posix(), file=name, expected=expected, actual=actual, match=actual == expected))
    raw = ROOT / 'datasets/Group3_Item2_Data/MANIFEST.txt'
    for line in raw.read_text(encoding='utf-8-sig').splitlines():
        parts = [s.strip() for s in line.split('|')]
        if len(parts) == 4 and len(parts[-1]) == 64:
            p = raw.parent / parts[0]; actual = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
            checks.append(dict(manifest=raw.relative_to(ROOT).as_posix(), file=parts[0], expected=parts[-1], actual=actual, match=actual == parts[-1]))
    save('manifest-verification.json', checks)
    versions = {}
    for p in sorted((ROOT / 'analysis').rglob('run_manifest.json')):
        if 'test_scratch.local' not in p.parts:
            versions[p.relative_to(ROOT).as_posix()] = json.loads(p.read_text(encoding='utf-8-sig'))
    for name in ('selected_model.json', 'forecast.json'):
        p = ROOT / 'analysis/outputs' / name
        if p.exists(): versions[p.relative_to(ROOT).as_posix()] = json.loads(p.read_text(encoding='utf-8-sig'))
    save('research-versions.json', versions)
    service = PlatformService()
    resources = []
    numeric_names = {'observed_value','count','rate','lower95','upper95','total_deaths','prediction','forecast','statistic_value','lower_limit','upper_limit','suspected_deaths'}
    for key in CATALOG:
        rows, metadata = service.artifacts.load(key)
        returned = []; offset = 0; pages = 0; total = None
        while True:
            env = service.query(key, Filters(limit=1000, offset=offset, signals_only=False))
            if total is None: total = env.total
            if total != env.total: raise RuntimeError('Changing resource total')
            returned.extend(env.data); pages += 1
            if len(returned) >= total: break
            if not env.data: raise RuntimeError('Incomplete resource')
            offset += len(env.data)
        fields = sorted(set().union(*(r.keys() for r in returned))) if returned else []
        numeric = [{k:r[k] for k in sorted(r) if k in numeric_names or (isinstance(r[k], (int,float)) and not isinstance(r[k], bool))} for r in returned]
        identity_fields = [k for k in ('observation_id','configuration_id','indicator_id','geography','period','year','quarter','method','model','window','origin_period','target_period','horizon') if k in fields]
        projection = [{k:r.get(k) for k in identity_fields} for r in returned]
        source_fields = ['geography','source_id','indicator_id','substance_category','source_population','reporting_definition','endpoint','outcome','quality_status','availability_status','status','publication_date','source_data_cutoff']
        resources.append(dict(resource=key, metadata=metadata, artifact_records=len(rows), api_records=len(returned), pages=pages,
                              complete=len(returned)==total, fields=fields, ordered_response_fingerprint=digest(returned),
                              numeric_field_projection_fingerprint=digest(numeric), numeric_projection_fields=sorted(set().union(*(r.keys() for r in numeric))) if numeric else [],
                              candidate_identity_fields=identity_fields, candidate_identity_duplicates=len(projection)-len({digest(r) for r in projection}),
                              candidate_identity_note='Diagnostic projection only; not a declared canonical key.',
                              source_scope_and_availability={k:sorted({json.dumps(r[k], sort_keys=True, ensure_ascii=False) for r in rows if k in r}, key=str) for k in source_fields if any(k in r for r in rows)},
                              null_by_field={k:sum(r.get(k) is None for r in returned) for k in fields},
                              definitions={k:sorted({json.dumps(r[k], sort_keys=True, ensure_ascii=False) for r in returned if k in r}, key=str) for k in ('unit','period_basis','reporting_definition','boundary_type','method','model','window','origin_period','target_period','forecast_origin','forecast_target','horizon','standard_population','rate_origin') if k in fields}))
    save('resource-contracts.json', resources)
    client = TestClient(create_app(service=service))
    save('openapi.json', client.get('/openapi.json').json())
    metadata_responses = {}
    for endpoint in ('health','geographies','indicators','methodology','validation/status','reports'):
        response = client.get('/api/v1/'+endpoint)
        metadata_responses[endpoint] = dict(http_status=response.status_code, body=response.json())
    save('metadata-responses.json', metadata_responses)
    save('capture-summary.json', dict(captured_at_utc=datetime.now(timezone.utc).isoformat(), resources=len(resources),
         manifest_checks=len(checks), manifest_matches=sum(x['match'] for x in checks),
         api_verification='In-process production PlatformService pagination plus ASGI metadata/OpenAPI GETs; not deployed HTTP availability.',
         fingerprints='SHA-256; ordered JSON projection, sorted keys, compact separators, UTF-8. CSV record fingerprints retain original strings. Numeric projections do not refit models.'))


if __name__ == '__main__':
    if '--verify' in sys.argv:
        before = json.loads((OUT / 'preservation-before.json').read_text(encoding='utf-8'))
        after = preservation()
        result = dict(files_before=len(before), files_after=len(after), added=sorted(after.keys()-before.keys()),
                      removed=sorted(before.keys()-after.keys()), changed=sorted(k for k in before.keys() & after.keys() if before[k] != after[k]))
        save('preservation-verification.json', result)
        print(json.dumps(result))
    else:
        capture()
        print('Baseline evidence captured in docs/baselines/task08b only.')
