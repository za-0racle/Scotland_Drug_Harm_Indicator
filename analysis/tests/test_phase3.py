import json

from analysis.phase3.audit import BASELINE, verify
from analysis.phase3.compatibility import compatible_calendar_quarter
from analysis.run import run


def test_phase2_hashes_values_and_metrics_agree():
    assert verify()['status'] == 'verified'


def test_phase2_run_reproduces_saved_baseline_without_overwriting_it(tmp_path):
    before = {path.name: path.read_bytes() for path in BASELINE.iterdir() if path.is_file()}
    timestamp = json.loads(before['run_manifest.json'])['executed_at_utc']
    run(tmp_path, timestamp)
    for name, content in before.items():
        assert (tmp_path / name).read_bytes() == content, name
        assert (BASELINE / name).read_bytes() == content, name


def test_non_calendar_and_unreviewed_outcomes_are_not_scored():
    for end in ('2026-08-30', '2026-08-31'):
        assert not compatible_calendar_quarter(dict(start='2026-06-01', end=end))
    assert not compatible_calendar_quarter(dict(start='2026-01-01', end='2026-03-31'))
    assert compatible_calendar_quarter(dict(start='2026-01-01', end='2026-03-31', definition_compatibility_reviewed=True, geography='Scotland national total'))
