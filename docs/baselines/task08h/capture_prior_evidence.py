"""Hash Task 08B–08G reports and evidence without modifying prior snapshots."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGETS = (
    ROOT / 'docs/TASK08C_MORTALITY_ADAPTER_REPORT.md',
    ROOT / 'docs/TASK08D_FRONTEND_MIGRATION_REPORT.md',
    ROOT / 'docs/TASK08E_FORENSIC_ADAPTER_REPORT.md',
    ROOT / 'docs/TASK08F_FORENSIC_FRONTEND_MIGRATION_REPORT.md',
    ROOT / 'docs/TASK08G_ARCHITECTURE_CONSOLIDATION_AUDIT.md',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (OUT / 'prior-evidence-before.json').exists():
        raise RuntimeError('Task 08H prior-evidence snapshot already exists; refusing to overwrite.')
    files = {}
    for path in TARGETS:
        files[path.relative_to(ROOT).as_posix()] = sha(path)
    for task in ('task08b', 'task08c', 'task08d', 'task08e', 'task08f'):
        for path in sorted((ROOT / 'docs/baselines' / task).rglob('*')):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = sha(path)
    output = OUT / 'prior-evidence-before.json'
    output.write_text(json.dumps(files, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'Captured {len(files)} prior reports and evidence files in {output.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
