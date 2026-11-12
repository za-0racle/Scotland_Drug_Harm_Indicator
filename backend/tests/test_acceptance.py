"""Phase 8 acceptance checks against unchanged research artifacts."""
from collections import Counter
import json
import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.services.platform import PlatformService
from backend.repositories.artifacts import ArtifactRepository
from backend.repositories.supabase import DatabaseError
from backend.schemas import Filters

@pytest.fixture(scope='module')
def service():return PlatformService()

@pytest.fixture(scope='module')
def client(service):return TestClient(create_app(service))

def test_every_supported_area_and_indicator_has_exact_source_rows(service):
    for area in service.registry.values():
        if not area['available']:continue
        listed=service.geography_data(area['geography_id'],'indicators',Filters(limit=1000))
        assert listed.data,area
        for indicator in listed.data:
            actual=service.geography_data(area['geography_id'],'trends',Filters(indicator=indicator['indicator_id'],limit=1000))
            expected=[r for r in service.artifacts.load(indicator['resource'])[0] if service.decorate(r).get('geography_id')==area['geography_id'] and r['indicator_id']==indicator['indicator_id']]
            assert actual.total==len(expected)>0,(area,indicator)
            assert [r['observed_value'] for r in actual.data]==[r['observed_value'] for r in expected]

def test_all_scientific_records_preserve_values(service):
    for resource in ['mortality_trends','forensic','assist','treatment','naloxone','annual','anomalies','enhanced','runs','forecast','rates','rate_comparisons']:
        original=service.artifacts.load(resource)[0]
        actual=[];position=0
        while True:
            page=service.query(resource,Filters(signals_only=False,offset=position,limit=1000))
            actual.extend(page.data);position+=len(page.data)
            if position>=page.total:break
        assert len(actual)==len(original),resource
        keys=set().union(*(row.keys() for row in original))
        encode=lambda rows:Counter(json.dumps({key:row.get(key) for key in keys},sort_keys=True,default=str) for row in rows)
        assert encode(actual)==encode(original),resource

def test_anomaly_flags_and_all_observations_are_chronological(service):
    flags=service.query('anomalies',Filters(indicator='suspected_deaths',limit=1000))
    assert flags.total==3
    assert [row['period_start'] for row in flags.data]==['2022-01-01','2022-04-01','2023-01-01']
    context=service.query('anomalies',Filters(indicator='suspected_deaths',signals_only=False,limit=1000))
    assert context.total>flags.total
    assert [row['period_start'] for row in context.data]==sorted(row['period_start'] for row in context.data)
    assert {row['classification'] for row in context.data}>={'insufficient_data','no_detected_anomaly','statistically_unusual_observation'}

def test_comparison_pages_bounded_complete_and_provenanced(service):
    boards=[a for a in service.registry.values() if a['boundary_type']=='health_board']
    left,right=boards[:2];gid=left['geography_id']
    indicator=next(i for i in left['indicators'] if i in right['indicators'])
    f=Filters(indicator=indicator,compare_to=right['geography_id'],limit=7)
    page=service.geography_data(gid,'comparisons',f)
    assert len(page.data)==7 and page.total==878
    assert page.metadata['artifact_sha256']
    following=service.geography_data(gid,'comparisons',f.model_copy(update={'offset':7}))
    assert following.total==878 and following.data!=page.data
    assert service.geography_data(gid,'comparisons',Filters(compare_to=right['geography_id'])).state=='unavailable'

def test_year_category_suppression_and_incompatible_indicators(service):
    rows=service.query('mortality_trends',Filters(signals_only=False,limit=1000)).data
    assert sum(r['observed_value'] is None for r in rows)==8
    f=service.query('forensic',Filters(category='Opioids',start_year=2026,end_year=2026,limit=1000))
    assert f.total==1 and f.data[0]['observed_value']==328
    council=next(a for a in service.registry.values() if a['boundary_type']=='council')
    assert service.geography_data(council['geography_id'],'trends',Filters(indicator='ambulance_naloxone_activity')).state=='unavailable'

def test_missing_artifact_returns_unavailable_not_fallback(tmp_path):
    c=TestClient(create_app(PlatformService(artifacts=ArtifactRepository(tmp_path))))
    response=c.get('/api/v1/mortality/annual')
    assert response.status_code==503 and response.json()['state']=='unavailable'
    assert not response.json()['data']

def test_export_exact_page_and_extra_query_rejection(client):
    params=dict(geography_id=next(a['geography_id'] for a in client.app.state.service.registry.values() if a['boundary_type']=='council'),start_year=2020,limit=2,offset=1)
    direct=client.get('/api/v1/mortality/annual',params=params).json()
    exported=client.get('/api/v1/exports',params=dict(params,resource='annual')).json()
    assert direct['data']==exported['data'] and exported['total']==5
    assert client.get('/api/v1/exports?resource=annual&filesystem=secret').status_code==422
