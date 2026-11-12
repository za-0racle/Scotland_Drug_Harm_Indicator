"""Workspace-local scratch directories with inherited Windows permissions.

Python's Windows mode-0700 temp directories are unreadable to the managed
workspace token. Ordinary inherited-permission directories avoid that issue.
Only test artifacts are stored here; *.local is already ignored by Git.
"""
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture
def tmp_path():
    base = Path(__file__).resolve().parents[1] / 'test_scratch.local'
    base.mkdir(exist_ok=True)
    directory = base / uuid4().hex
    directory.mkdir()
    return directory
