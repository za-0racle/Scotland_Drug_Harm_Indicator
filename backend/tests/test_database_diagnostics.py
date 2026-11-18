import io
import json
import logging
from urllib.error import URLError,HTTPError
import pytest
from backend.config import Settings
from backend.repositories.supabase import SupabaseRepository,DatabaseError


class Reply(io.BytesIO):
    headers={'Content-Range':'0-0/1'}


@pytest.mark.parametrize('paged',[True])
def test_transport_failure_is_sanitised_and_next_read_recovers(caplog,paged):
    calls=[]
    def opener(request,timeout):
        calls.append(1)
        if len(calls)==1:raise URLError(TimeoutError('SECRET_SENTINEL URL and credential must never enter logs'))
        row={'area_code':'TEST','area_name':'Test area','area_type':'council','valid_from':'2020-01-01','valid_to':None,'source_dataset':'test fixture'} if paged else {'year':2024,'quarter':1,'suspected_deaths':1}
        return Reply(json.dumps([row]).encode())
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST_SECRET_SENTINEL'),opener)
    read=(lambda:repo.read_page('geographic_areas',0,1)) if paged else (lambda:repo.read('mortality_quarterly'))
    with caplog.at_level(logging.ERROR),pytest.raises(DatabaseError,match='Supabase read failed'):
        read()
    assert len(calls)==1  # No concealed retry or fallback.
    assert 'category=timeout' in caplog.text and 'reason_type=TimeoutError' in caplog.text
    assert 'SECRET_SENTINEL' not in caplog.text and 'https://' not in caplog.text
    assert read()


def test_http_permission_failure_remains_an_error_without_retry(caplog):
    calls=[]
    def opener(request,timeout):
        calls.append(1)
        raise HTTPError('https://sensitive.invalid',403,'SECRET_SENTINEL',{},None)
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST'),opener)
    with caplog.at_level(logging.ERROR),pytest.raises(DatabaseError):repo.read('mortality_quarterly')
    assert len(calls)==1 and 'http_status=403' in caplog.text and 'category=http' in caplog.text
    assert 'SECRET_SENTINEL' not in caplog.text and 'sensitive.invalid' not in caplog.text


def test_single_connection_timeout_is_logged_and_recovered_without_altering_values(caplog):
    calls=[]
    expected=[{'year':2024,'quarter':1,'suspected_deaths':1}]
    def opener(request,timeout):
        calls.append(timeout)
        if len(calls)==1:raise URLError(TimeoutError('SECRET_SENTINEL'))
        return Reply(json.dumps(expected).encode())
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST'),opener)
    with caplog.at_level(logging.INFO):assert repo.read('mortality_quarterly')==expected
    assert calls==[12,12]
    assert 'database_read_retry' in caplog.text and 'database_read_recovered' in caplog.text
    assert 'SECRET_SENTINEL' not in caplog.text


def test_persistent_connection_timeout_remains_visible_after_exactly_two_attempts(caplog):
    calls=[]
    def opener(request,timeout):
        calls.append(timeout)
        raise URLError(TimeoutError('SECRET_SENTINEL'))
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST'),opener)
    with caplog.at_level(logging.ERROR),pytest.raises(DatabaseError,match='Supabase read failed'):
        repo.read('mortality_quarterly')
    assert calls==[12,12] and caplog.text.count('database_read_failed')==2
    assert 'SECRET_SENTINEL' not in caplog.text


def test_invalid_json_is_not_retried(caplog):
    calls=[]
    def opener(request,timeout):calls.append(1);return Reply(b'not json')
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST'),opener)
    with pytest.raises(DatabaseError):repo.read('mortality_quarterly')
    assert calls==[1] and 'category=json' in caplog.text
