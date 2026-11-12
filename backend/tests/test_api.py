import io
import json
import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.config import Settings,ROOT
from backend.services.platform import PlatformService
from backend.repositories.artifacts import ArtifactRepository,ArtifactError
from backend.repositories.supabase import SupabaseRepository,DatabaseError

class FakeDatabase:
    def read(self,table):
        return [dict(year=2024,quarter=1,suspected_deaths=123)] # Synthetic test fixture, not real dashboard data.

@pytest.fixture(scope='module')
def client():return TestClient(create_app(PlatformService(database=FakeDatabase())))

def test_health_schema_overview_and_database_mapping(client):
    assert client.get('/api/v1/health').json()['data'][0]['api']=='ok'
    overview=client.get('/api/v1/overview').json()['data'][0]
    assert overview['database']['kind']=='database_observation'
    response=client.get('/api/v1/mortality/quarterly').json()
    assert response['kind']=='database_observation' and response['data'][0]['suspected_deaths']==123

def test_dynamic_geography_coverage_and_boundary_compatibility(client):
    areas=client.get('/api/v1/geographies').json()['data']
    assert sum(a['boundary_type']=='police_division' for a in areas)==13
    assert sum(a['boundary_type']=='health_board' for a in areas)==14
    greenock=next(a for a in areas if a['name']=='Greenock')
    assert client.get(f"/api/v1/geographies/{greenock['geography_id']}/trends").json()['state']=='unavailable'
    police=next(a for a in areas if a['boundary_type']=='police_division')
    board=next(a for a in areas if a['boundary_type']=='health_board')
    assert client.get(f"/api/v1/geographies/{police['geography_id']}/comparisons",params={'compare_to':board['geography_id']}).status_code==422
    assert client.get('/api/v1/geographies/not-a-valid-area').status_code==422

def test_artifact_values_provenance_filters_and_pagination(client):
    response=client.get('/api/v1/mortality/annual',params={'start_year':2024,'end_year':2024,'limit':1}).json()
    assert response['total']==2 and len(response['data'])==1
    assert response['data'][0]['observed_value']==25
    assert response['metadata']['artifact_sha256'] and response['metadata']['analytical_version']=='phase6-1.0.0'
    assert client.get('/api/v1/mortality/annual?limit=1001').status_code==422
    assert client.get('/api/v1/mortality/annual?start_year=2024&end_year=2020').status_code==422
    assert client.get('/api/v1/mortality/annual?arbitrary_sql=select').status_code==422
    assert client.get('/api/v1/mortality/annual?start_year=2099').json()['state']=='empty'

def test_original_flags_sensitivity_models_runs_and_real_evidence(client):
    assert client.get('/api/v1/anomalies?limit=1000').json()['total']==47
    assert client.get('/api/v1/anomalies/runs?model=phase5_robust').json()['total']==44
    assert client.get('/api/v1/anomalies/sensitivity').json()['total']==7878
    assert client.get('/api/v1/evidence/cross-source').json()['total']==4512
    r=client.get('/api/v1/anomalies?model=nb2_moments').json()
    assert r['total']==40 and all(x['signal'] for x in r['data'])

def test_case_study_forecast_and_external_validation(client):
    case=client.get('/api/v1/geography/inverclyde').json()['data'][0]
    assert case['findings']['latest']['observed_value']==25
    rate=case['findings']['latest_published_rate_comparison']
    assert (rate['inverclyde_rate'],rate['inverclyde_lower95'],rate['inverclyde_upper95'])==(35.6,29.3,41.8)
    forecast=client.get('/api/v1/forecasting/results').json()['data'][0]
    assert forecast['forecast_origin']=='2025 Q4' and forecast['target_period']=='2026 Q1'
    assert client.get('/api/v1/validation/status').json()['data'][0]['external_alert_metrics']=='unavailable'

def test_export_allowlist_and_preserved_metadata(client):
    r=client.get('/api/v1/exports?resource=annual&format=csv&limit=1')
    assert r.status_code==200 and '_analytical_version' in r.text and '_limitations' in r.text
    assert client.get('/api/v1/exports?resource=../../.env.local').status_code==422
    assert client.get('/api/v1/exports?resource=radar_intelligence').status_code==422
    assert client.post('/api/v1/anomalies').status_code==405
    assert client.get('/api/v1/reports').status_code==200

def test_database_failure_empty_rls_and_no_secret_error():
    class Failing:
        def read(self,table):raise DatabaseError('Supabase read failed; check backend connectivity and approved RLS access')
    c=TestClient(create_app(PlatformService(database=Failing())))
    assert c.get('/api/v1/mortality/quarterly').status_code==503
    assert c.get('/api/v1/overview').json()['data'][0]['database']['state']=='error'
    class Empty:
        def read(self,table):return []
    c=TestClient(create_app(PlatformService(database=Empty())))
    assert c.get('/api/v1/mortality/quarterly').json()['state']=='empty'

def test_cors_and_no_filesystem_or_sql_api(client):
    assert client.get('/api/v1/health',headers={'Origin':'https://untrusted.example'}).headers.get('access-control-allow-origin') is None
    assert client.get('/api/v1/health',headers={'Origin':'http://localhost:5173'}).headers['access-control-allow-origin']=='http://localhost:5173'
    assert client.get('/api/v1/private/raw_sql').status_code==404

def test_artifact_corruption_rejected(tmp_path):
    directory=tmp_path/'analysis/phase6/outputs';directory.mkdir(parents=True)
    (directory/'validated_geographic_observations.csv').write_text('geography,indicator_id,observed_value\nTEST,TEST,1\n')
    (directory/'run_manifest.json').write_text(json.dumps({'output_hashes':{'validated_geographic_observations.csv':'wrong'}}))
    with pytest.raises(ArtifactError):ArtifactRepository(tmp_path).load('annual')
    with pytest.raises(ArtifactError):ArtifactRepository().load('../../.env.local')

def test_repository_explicit_columns_caps_and_credentials():
    seen=[]
    class Reply(io.BytesIO):
        headers={'Content-Range':'0-0/1'}
    def opener(req,timeout):seen.append(req);return Reply(b'[{"year":2024,"quarter":1,"suspected_deaths":1}]')
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST_FIXTURE'),opener)
    assert len(repo.read('mortality_quarterly'))==1
    assert 'select=year%2Cquarter%2Csuspected_deaths' in seen[0].full_url
    assert seen[0].get_method()=='GET'
    with pytest.raises(DatabaseError):repo.read('radar_intelligence')
    with pytest.raises(DatabaseError):SupabaseRepository(Settings('https://test.supabase.co','sb_secret_TEST')).read('mortality_quarterly')
    with pytest.raises(DatabaseError):SupabaseRepository(Settings()).read('mortality_quarterly')
    class Capped(Reply):headers={'Content-Range':'0-0/10'}
    with pytest.raises(DatabaseError):SupabaseRepository(repo.settings,lambda *a,**k:Capped(b'[{}]')).read('mortality_quarterly')

def test_all_declared_get_contracts(client):
    for path in ['/sources','/methodology','/validation/status','/toxicology/forensic','/toxicology/assist','/toxicology/treatment','/naloxone/activity','/anomalies/models','/anomalies/diagnostics','/anomalies/zero-baseline','/forecasting/models','/forecasting/backtest','/forecasting/observations','/geography/comparisons','/monitoring/configurations','/monitoring/results']:
        response=client.get('/api/v1'+path)
        assert response.status_code==200,(path,response.text[:100])
        assert isinstance(response.json()['data'],list)


def test_refresh_refuses_existing_or_public_destinations(tmp_path):
    from backend.refresh import refresh
    with pytest.raises(ValueError):refresh('phase6',ROOT/'analysis/phase6/outputs')
    with pytest.raises(ValueError):refresh('phase6',tmp_path)
    with pytest.raises(ValueError):refresh('unreviewed',tmp_path)
