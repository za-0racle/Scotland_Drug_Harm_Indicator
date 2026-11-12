from pathlib import Path
from uuid import uuid4
import pytest

@pytest.fixture
def tmp_path():
    directory=Path(__file__).resolve().parents[2]/'analysis/test_scratch.local'/uuid4().hex
    directory.mkdir(parents=True,exist_ok=True)
    return directory
