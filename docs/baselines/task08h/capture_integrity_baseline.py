"""Capture current analytical API bytes and integrity outputs without overwrites."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from backend.main import create_app

OUT = Path(__file__).resolve().parent
MORTALITY = '/api/v1/analytical/v1/mortality-trends'
FORENSIC = '/api/v1/analytical/v1/forensic-toxicology'
EXPECTED = {
    'mortality': {
        'token': 'f8dfefd52958a19e275bf1e055aa5e0b2b3f540afa6a392687c759a79373568f',
        'total': 504,
    },
    'forensic': {
        'token': 'e195aa5753ca3b6c047109eab9ea83b39554a185fb968748771df96b442c3722',
        'total': 210,
    },
}


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def write_new(name, content):
    path = OUT / name
    with path.open('xb') as handle:
        handle.write(content)
    return path


def canonical_payload(resource, response):
    if resource == 'mortality':
        keys = ('contract_version', 'source', 'indicator', 'artifact', 'research_metadata', 'observations')
    else:
        keys = ('contract_version', 'source', 'artifact', 'measure', 'categories', 'research_metadata', 'observations')
    payload = {key: response[key] for key in keys}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if digest_bytes(encoded) != response['pagination']['collection_token']:
        raise AssertionError(f'{resource} canonical content does not match its collection token')
    return encoded


def collect(client, resource, path):
    evidence = EXPECTED[resource]
    first = client.get(path, params={'limit': 1000})
    first.raise_for_status()
    full_bytes = first.content
    full = first.json()
    if full['pagination']['collection_token'] != evidence['token'] or full['pagination']['total'] != evidence['total']:
        raise AssertionError(f'{resource} no longer matches approved pre-change evidence')

    fixture_path = ROOT / ('docs/baselines/task08d/contract-response.json'
                           if resource == 'mortality'
                           else 'docs/baselines/task08f/analytical-response.json')
    fixture = json.loads(fixture_path.read_bytes())
    if full != fixture:
        raise AssertionError(f'{resource} live API does not reconcile to the approved fixture')

    paged = []
    observations = []
    offset = 0
    while offset < evidence['total']:
        params = {'offset': offset, 'limit': 73}
        if offset:
            params['expected_collection'] = evidence['token']
        response = client.get(path, params=params)
        response.raise_for_status()
        page = response.json()
        if page['pagination']['collection_token'] != evidence['token']:
            raise AssertionError(f'{resource} pagination changed collection token')
        if page['pagination']['offset'] != offset:
            raise AssertionError(f'{resource} pagination offset mismatch')
        observations.extend(page['observations'])
        paged.append(response.content)
        offset += page['pagination']['returned']
    if observations != full['observations']:
        raise AssertionError(f'{resource} paginated observations differ from complete page')

    canonical = canonical_payload(resource, full)
    write_new(f'{resource}-response-1000.json', full_bytes)
    write_new(f'{resource}-canonical-payload.json', canonical)
    jsonl = b'\n'.join(paged) + b'\n'
    write_new(f'{resource}-pages-73.jsonl', jsonl)
    identities = {
        'collection_token': evidence['token'],
        'observation_ids': [row['observation_id'] for row in full['observations']],
        'category_ids': [category['category_id'] for category in full.get('categories', [])],
    }
    write_new(f'{resource}-identities.json', (json.dumps(identities, ensure_ascii=False, indent=2) + '\n').encode())
    return {
        'response_sha256': digest_bytes(full_bytes),
        'response_bytes': len(full_bytes),
        'canonical_payload_sha256': digest_bytes(canonical),
        'canonical_payload_bytes': len(canonical),
        'page_sequence_sha256': digest_bytes(jsonl),
        'page_sequence_bytes': len(jsonl),
        'page_count_limit_73': len(paged),
        'collection_token': evidence['token'],
        'observations': len(full['observations']),
        'first_observation_id': full['observations'][0]['observation_id'],
        'observation_ids_sha256': digest_bytes(json.dumps(identities['observation_ids'], separators=(',', ':')).encode()),
        'category_ids_sha256': digest_bytes(json.dumps(identities['category_ids'], separators=(',', ':')).encode()),
        'source_version': full['source']['source_version'],
        'artifact_version': full['artifact']['analytical_version'],
        'artifact_sha256': full['artifact']['artifact_sha256'],
    }


def main():
    if any(path.name != Path(__file__).name for path in OUT.iterdir()):
        raise RuntimeError('Task 08H evidence directory is not empty; refusing to overwrite.')
    with TestClient(create_app()) as client:
        results = {
            'mortality': collect(client, 'mortality', MORTALITY),
            'forensic': collect(client, 'forensic', FORENSIC),
        }
    source_path = ROOT / 'datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv'
    artifact_path = ROOT / 'analysis/phase4/outputs/forensic_counts.csv'
    mortality_artifact_path = ROOT / 'analysis/phase4/outputs/mortality_quarterly.csv'
    references = {
        'task08b_manifest_verification_sha256': digest_bytes((ROOT / 'docs/baselines/task08b/manifest-verification.json').read_bytes()),
        'task08d_legacy_response_sha256': digest_bytes((ROOT / 'docs/baselines/task08d/legacy-response.json').read_bytes()),
        'task08f_legacy_response_sha256': digest_bytes((ROOT / 'docs/baselines/task08f/legacy-response.json').read_bytes()),
        'task08f_legacy_screen_export_sha256': digest_bytes((ROOT / 'docs/baselines/task08f/legacy-screen-export.csv').read_bytes()),
        'forensic_source_sha256': digest_bytes(source_path.read_bytes()),
        'forensic_artifact_sha256': digest_bytes(artifact_path.read_bytes()),
        'mortality_artifact_sha256': digest_bytes(mortality_artifact_path.read_bytes()),
        'task08d_legacy_frontend_records_sha256': digest_bytes((ROOT / 'docs/baselines/task08d/legacy-response.json').read_bytes()),
        'task08f_legacy_frontend_records_sha256': digest_bytes((ROOT / 'docs/baselines/task08f/legacy-response.json').read_bytes()),
    }
    summary = {'capture': 'pre-Task-08H source behavior', 'contracts': results, 'independent_references': references}
    write_new('capture-summary.json', (json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
