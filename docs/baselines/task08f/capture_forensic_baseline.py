"""Read-only pre-migration capture for Task 08F; refuses to overwrite evidence."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from backend.config import ROOT as CONFIG_ROOT
from backend.main import create_app
from backend.services.mortality_adapter import fingerprint
from fastapi.testclient import TestClient


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    if CONFIG_ROOT != ROOT:
        raise SystemExit('Unexpected workspace root; capture refused.')
    names = ('legacy-response.json', 'analytical-response.json', 'capture-summary.json')
    if any((OUT / name).exists() for name in names):
        raise SystemExit('Task 08F evidence already exists; capture refused without overwriting.')

    baseline_08b = ROOT / 'docs/baselines/task08b'
    baseline_08e = ROOT / 'docs/baselines/task08e/forensic-baseline.json'
    old_contracts = json.loads((baseline_08b / 'resource-contracts.json').read_text(encoding='utf-8'))
    forensic_08b = next(item for item in old_contracts if item['resource'] == 'forensic')
    evidence_08e = json.loads(baseline_08e.read_text(encoding='utf-8'))
    if (fingerprint(evidence_08e['response']['data']) != forensic_08b['ordered_response_fingerprint']
            or evidence_08e['response']['metadata'] != forensic_08b['metadata']
            or not all(evidence_08e['task08b_comparisons'].values())
            or len(evidence_08e['manifest_checks']) != 85
            or not all(item['match'] for item in evidence_08e['manifest_checks'])):
        raise SystemExit('Task 08B/08E forensic baseline discrepancy; capture stopped.')

    client = TestClient(create_app())
    legacy = client.get('/api/v1/toxicology/forensic', params={'offset': 0, 'limit': 1000}).json()
    if (legacy['total'] != 210 or len(legacy['data']) != 210
            or fingerprint(legacy['data']) != forensic_08b['ordered_response_fingerprint']
            or legacy['metadata'] != forensic_08b['metadata']):
        raise SystemExit('Current legacy forensic response differs from immutable Task 08B evidence.')

    first = client.get('/api/v1/analytical/v1/forensic-toxicology', params={'offset': 0, 'limit': 1000})
    if first.status_code != 200:
        raise SystemExit(f'Current Task 08E analytical route failed: HTTP {first.status_code}.')
    analytical = first.json()
    if (analytical['contract_version'] != 'forensic-toxicology/1.0.0'
            or analytical['pagination']['total'] != 210
            or len(analytical['observations']) != 210
            or not analytical['pagination']['page_is_complete_collection']):
        raise SystemExit('Current Task 08E response is incomplete or unsupported.')

    for name, value in (('legacy-response.json', legacy), ('analytical-response.json', analytical)):
        (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    summary = {
        'legacy_response_sha256': sha256(OUT / 'legacy-response.json'),
        'analytical_response_sha256': sha256(OUT / 'analytical-response.json'),
        'legacy_ordered_response_fingerprint': forensic_08b['ordered_response_fingerprint'],
        'legacy_numeric_fingerprint': forensic_08b['numeric_field_projection_fingerprint'],
        'legacy_artifact_sha256': forensic_08b['metadata']['artifact_sha256'],
        'source_sha256': evidence_08e['source_sha256'],
        'observations': len(analytical['observations']),
        'categories': [item['original_label'] for item in analytical['categories']],
        'quarters': sorted({item['period']['original_label'] for item in analytical['observations']}),
        'null_values': sum(item['value'] is None for item in analytical['observations']),
        'zero_values': sum(item['value'] == 0 for item in analytical['observations']),
        'task08b_checks_passed': evidence_08e['task08b_comparisons'],
        'source_research_manifest_checks': len(evidence_08e['manifest_checks']),
    }
    (OUT / 'capture-summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
