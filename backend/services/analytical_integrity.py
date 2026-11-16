"""Source-neutral integrity primitives for versioned analytical resources."""
import hashlib
import json


def fingerprint(value):
    """SHA-256 of the repository's canonical UTF-8 JSON representation."""
    return hashlib.sha256(json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':'),
        allow_nan=False,
    ).encode()).hexdigest()


def relative_path(path):
    """Preserve the existing relative provenance-path acceptance rules."""
    if not isinstance(path, str) or path.startswith(('/', '\\')) or '\\' in path or ':' in path or '..' in path.split('/'):
        raise ValueError('Invalid relative provenance path')
    return path
