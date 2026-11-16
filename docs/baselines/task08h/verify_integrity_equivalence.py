"""Verify extracted integrity primitives against immutable pre-change evidence."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from backend.main import create_app
from backend.services.analytical_integrity import fingerprint

OUT = Path(__file__).resolve().parent
CAPTURE = json.loads((OUT / 'capture-summary.json').read_text(encoding='utf-8'))
ROUTES = {
    'mortality': '/api/v1/analytical/v1/mortality-trends',
    'forensic': '/api/v1/analytical/v1/forensic-toxicology',
}
FIXTURES = {
    'mortality': ROOT / 'docs/baselines/task08d/contract-response.json',
    'forensic': ROOT / 'docs/baselines/task08f/analytical-response.json',
}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def token_payload(resource, response):
    keys = ('contract_version', 'source', 'indicator', 'artifact', 'research_metadata', 'observations') \
        if resource == 'mortality' else (
            'contract_version', 'source', 'artifact', 'measure', 'categories', 'research_metadata', 'observations'
        )
    return {key: response[key] for key in keys}


def verify_resource(client, name):
    pre = CAPTURE['contracts'][name]
    route = ROUTES[name]
    first = client.get(route, params={'limit': 1000})
    first.raise_for_status()
    full = first.json()
    before_bytes = (OUT / f'{name}-response-1000.json').read_bytes()
    if first.content != before_bytes:
        raise AssertionError(f'{name} API JSON response bytes changed')
    if full != json.loads(FIXTURES[name].read_bytes()):
        raise AssertionError(f'{name} response differs from the approved immutable fixture')
    canonical = json.dumps(token_payload(name, full), sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False).encode('utf-8')
    canonical_before = (OUT / f'{name}-canonical-payload.json').read_bytes()
    if canonical != canonical_before or fingerprint(token_payload(name, full)) != pre['collection_token']:
        raise AssertionError(f'{name} canonical JSON/token changed')
    if full['pagination']['collection_token'] != pre['collection_token']:
        raise AssertionError(f'{name} collection token changed')
    identities = json.loads((OUT / f'{name}-identities.json').read_text(encoding='utf-8'))
    actual_ids = [row['observation_id'] for row in full['observations']]
    if actual_ids != identities['observation_ids']:
        raise AssertionError(f'{name} observation identities changed')
    if sha(json.dumps(actual_ids, separators=(',', ':')).encode()) != pre['observation_ids_sha256']:
        raise AssertionError(f'{name} observation identity fingerprint changed')
    categories = [category['category_id'] for category in full.get('categories', [])]
    if categories != identities['category_ids']:
        raise AssertionError(f'{name} category identities changed')
    if sha(json.dumps(categories, separators=(',', ':')).encode()) != pre['category_ids_sha256']:
        raise AssertionError(f'{name} category identity fingerprint changed')

    observations = []
    page_bytes = []
    offset = 0
    while offset < full['pagination']['total']:
        params = {'offset': offset, 'limit': 73}
        if offset:
            params['expected_collection'] = pre['collection_token']
        response = client.get(route, params=params)
        response.raise_for_status()
        page = response.json()
        if page['pagination']['offset'] != offset:
            raise AssertionError(f'{name} pagination offset changed')
        if page['pagination']['collection_token'] != pre['collection_token']:
            raise AssertionError(f'{name} page token changed')
        if page['pagination']['returned'] != len(page['observations']):
            raise AssertionError(f'{name} page record count changed')
        observations.extend(page['observations'])
        page_bytes.append(response.content)
        offset += page['pagination']['returned']
    if observations != full['observations']:
        raise AssertionError(f'{name} page sequence differs from the complete response')
    page_sequence = b'\n'.join(page_bytes) + b'\n'
    if page_sequence != (OUT / f'{name}-pages-73.jsonl').read_bytes():
        raise AssertionError(f'{name} pagination response bytes changed')
    if len(page_bytes) != pre['page_count_limit_73']:
        raise AssertionError(f'{name} page count changed')

    if len(actual_ids) != pre['observations']:
        raise AssertionError(f'{name} observation count changed')
    return {
        'response_bytes_match': True,
        'fixture_json_matches': True,
        'canonical_payload_bytes_match': True,
        'collection_token_match': True,
        'observation_identities_match': len(actual_ids),
        'category_identities_match': len(categories),
        'page_sequence_bytes_match': True,
        'page_count_limit_73': len(page_bytes),
    }


def verify_research_integrity():
    entries = json.loads((ROOT / 'docs/baselines/task08b/manifest-verification.json').read_text(encoding='utf-8'))
    for entry in entries:
        manifest_dir = Path(entry['manifest']).parent
        path = ROOT / manifest_dir / entry['file']
        if not path.is_file() or sha(path.read_bytes()) != entry['expected']:
            raise AssertionError(f'Source/research manifest mismatch: {path.relative_to(ROOT)}')
    if len(entries) != 85:
        raise AssertionError(f'Expected 85 manifests, found {len(entries)}')

    e8 = json.loads((ROOT / 'docs/baselines/task08e/forensic-baseline.json').read_text(encoding='utf-8'))
    refs = CAPTURE['independent_references']
    paths = {
        'forensic_source_sha256': ROOT / 'datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv',
        'forensic_artifact_sha256': ROOT / 'analysis/phase4/outputs/forensic_counts.csv',
        'mortality_artifact_sha256': ROOT / 'analysis/phase4/outputs/mortality_quarterly.csv',
    }
    for key, path in paths.items():
        if sha(path.read_bytes()) != refs[key]:
            raise AssertionError(f'Frozen source/artifact changed: {path.relative_to(ROOT)}')
    if refs['forensic_source_sha256'] != e8['source_sha256']:
        raise AssertionError('Forensic source hash differs from immutable Task 08E evidence')

    before = json.loads((OUT / 'prior-evidence-before.json').read_text(encoding='utf-8'))
    for relative, expected in before.items():
        path = ROOT / relative
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise AssertionError(f'Prior Task 08B–08G evidence changed: {relative}')
    return {'source_research_manifests': len(entries), 'prior_evidence_files': len(before),
            'frozen_source_and_artifact_hashes': len(paths)}


def main():
    if (OUT / 'verification-summary.json').exists():
        raise RuntimeError('Task 08H verification evidence exists; refusing to overwrite.')
    with TestClient(create_app()) as client:
        results = {name: verify_resource(client, name) for name in ROUTES}
    preservation = verify_research_integrity()
    output = {'post_change_equivalence': results, 'preservation': preservation}
    (OUT / 'verification-summary.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
