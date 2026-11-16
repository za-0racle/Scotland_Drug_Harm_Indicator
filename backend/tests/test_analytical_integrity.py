import math

import pytest

from backend.services.analytical_integrity import fingerprint, relative_path
from backend.services.mortality_adapter import (
    fingerprint as mortality_fingerprint,
    relative_path as mortality_relative_path,
)


def test_existing_mortality_module_helper_imports_remain_compatible():
    assert mortality_fingerprint is fingerprint
    assert mortality_relative_path is relative_path


def test_fingerprint_preserves_python_json_encoding_and_sha256():
    nested = {
        'z': '\u00e9',
        'a': {'\u03b2': [1, 1.0, -0.0, None, True]},
        'n': 1e-7,
    }
    assert fingerprint(nested) == '9c60901103a20f1b621c74c159467255ada2f0bb237323de81293767ee91b1c8'
    assert fingerprint({'b': 2, 'a': 1}) == '43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777'


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_fingerprint_rejects_nonfinite_numbers(value):
    with pytest.raises(ValueError):
        fingerprint({'value': value})


@pytest.mark.parametrize('path', ['', 'a', 'a/b', 'a/./b', 'a//b'])
def test_relative_path_preserves_existing_accepted_forms(path):
    assert relative_path(path) == path


@pytest.mark.parametrize('path', ['/a', '\\a', 'a\\b', 'a/../b', 'C:/a', None, 1])
def test_relative_path_preserves_existing_rejections(path):
    with pytest.raises(ValueError, match='Invalid relative provenance path'):
        relative_path(path)
