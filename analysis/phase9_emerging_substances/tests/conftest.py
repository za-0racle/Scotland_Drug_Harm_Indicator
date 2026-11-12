from pathlib import Path
from uuid import uuid4
import pytest

@pytest.fixture
def tmp_path():
    path=Path(__file__).resolve().parents[2]/'test_scratch.local'/('phase9_'+uuid4().hex)
    path.mkdir(parents=True)
    return path
