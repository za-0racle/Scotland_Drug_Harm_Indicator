"""Explicit local-only analytical refresh into a new private scratch directory."""
import argparse
import importlib
from pathlib import Path
from backend.config import ROOT

def refresh(phase, destination):
    allowed={'phase4','phase5','phase5c','phase6'}
    if phase not in allowed:raise ValueError('Unsupported refresh phase')
    base=(ROOT/'analysis/test_scratch.local/phase7_refresh').resolve()
    target=Path(destination).resolve()
    if not target.is_relative_to(base) or target==base or target.exists():
        raise ValueError('Use a new directory beneath analysis/test_scratch.local/phase7_refresh')
    target.parent.mkdir(parents=True,exist_ok=True)
    return importlib.import_module('analysis.'+phase+'.run').run(target)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['phase4','phase5','phase5c','phase6'])
    parser.add_argument('destination')
    args=parser.parse_args();refresh(args.phase,args.destination)
    print('Private scratch run completed; no API catalogue promotion or database publication performed')
