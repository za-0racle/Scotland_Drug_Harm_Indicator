"""Task 08C: compare to immutable 08B fingerprints, not only current inputs."""
import copy
import json
import pytest
from fastapi.testclient import TestClient
from backend.config import ROOT
from backend.main import create_app
from backend.repositories.artifacts import ArtifactRepository, ArtifactError
from backend.services.analytical_integrity import fingerprint
from backend.services.platform import PlatformService
from backend.services.mortality_adapter import (
    MortalityAdapter, CollectionConflict, collect_pages, observation_identity,
)

BASELINE = ROOT / 'docs/baselines/task08b'


def evidence(name):
    return json.loads((BASELINE / name).read_text(encoding='utf-8'))


def resource_evidence():
    return next(r for r in evidence('resource-contracts.json') if r['resource'] == 'mortality_trends')


@pytest.fixture(scope='module')
def adapter():
    return MortalityAdapter(ArtifactRepository())


@pytest.fixture(scope='module')
def complete(adapter):
    return adapter.page(limit=1000)


def legacy_record(page, observation, decorated=True):
    """Lossless inverse for the existing frozen fields; no source rows read."""
    s, i, a, o = page.source, page.indicator, page.artifact, observation
    row = dict(indicator_id=i.indicator_id, source_id=s.source_id, source_path=s.source_path,
               geography=o.geography.original_name, period=o.period.label, ordinal=o.period.ordinal,
               observed_value=o.value, unit=i.unit, period_basis=i.period_basis,
               period_start=o.period.period_start, period_end=o.period.period_end,
               quality_status=o.availability_status, limitations=i.original_reporting_qualification,
               year=o.period.year, quarter=o.period.quarter, publication_date=s.publication_date,
               rolling_periods=i.rolling_periods, reference_periods=i.reference_periods,
               year_comparison_basis=i.year_comparison_basis, calculation_method=i.calculation_method,
               source_sha256=s.source_version, source_url=s.source_url, source_data_cutoff=s.source_data_cutoff,
               publication_status=s.publication_status, scientific_status=i.scientific_status,
               **page.research_metadata.model_dump(), **o.research_context.model_dump())
    if decorated:
        row.update(geography_id=o.geography.geography_id, name=o.geography.canonical_name,
                   boundary_type=o.geography.boundary_type, source_geography=o.geography.original_name)
    return row


def test_all_slots_values_nulls_labels_provenance_match_immutable_response(complete):
    baseline = resource_evidence()
    reconstructed = [legacy_record(complete, o) for o in complete.observations]
    assert len(reconstructed) == baseline['api_records'] == 504
    assert sorted(reconstructed[0]) == baseline['fields']
    # Hash covers every field/value, not just value totals or another live transform.
    assert fingerprint(reconstructed) == baseline['ordered_response_fingerprint']
    assert {k:sum(r.get(k) is None for r in reconstructed) for k in baseline['fields']} == baseline['null_by_field']
    assert sum(o.value is None for o in complete.observations) == 8
    assert sum(o.availability_status == 'missing_or_suppressed' for o in complete.observations) == 8
    assert complete.artifact.model_dump() == baseline['metadata']


def test_numerical_fingerprint_matches_immutable_evidence(complete):
    baseline = resource_evidence()
    numerical_names = {'observed_value','count','rate','lower95','upper95','total_deaths','prediction','forecast','statistic_value','lower_limit','upper_limit','suspected_deaths'}
    rows = [legacy_record(complete, o) for o in complete.observations]
    projection = [{k:r[k] for k in sorted(r) if k in numerical_names or isinstance(r[k], (int,float)) and not isinstance(r[k],bool)} for r in rows]
    assert fingerprint(projection) == baseline['numeric_field_projection_fingerprint']


def test_original_csv_records_and_identities_match_baseline(complete):
    records = [legacy_record(complete, o, decorated=False) for o in complete.observations]
    strings = [{k:'' if v is None else str(v) for k,v in r.items()} for r in records]
    stored = next(r for r in evidence('file-inventory.json') if r['path'] == complete.artifact.source_path)
    assert fingerprint(strings) == stored['ordered_record_fingerprint']
    identity = next(r for r in evidence('identity-verification.json') if r['resource'] == 'mortality_trends')
    assert fingerprint([{k:r[k] for k in identity['fields']} for r in records]) == identity['ordered_identity_fingerprint']
    assert len({o.observation_id for o in complete.observations}) == 504


def test_old_export_still_matches_baseline_and_old_openapi_paths():
    client = TestClient(create_app())
    result = client.get('/api/v1/exports', params={'resource':'mortality_trends','format':'json','limit':1000}).json()
    assert fingerprint(result['data']) == resource_evidence()['ordered_response_fingerprint']
    old = evidence('openapi.json')
    current = client.get('/openapi.json').json()
    for path, definition in old['paths'].items():
        assert current['paths'][path] == definition
    assert set(current['paths']) - set(old['paths']) == {
        '/api/v1/analytical/v1/mortality-trends',
        '/api/v1/analytical/v1/forensic-toxicology',
        '/api/v1/database/v1/data-sources',
        '/api/v1/database/v1/geographic-areas',
        '/api/v1/database/v1/naloxone-activity',
        '/api/v1/forecasting/generate',
        '/api/v1/forecasting/options',
    }


@pytest.mark.parametrize('size', [1, 73, 1000])
def test_complete_pagination_and_verified_collector(adapter, size):
    pages = []; offset = 0; token = None
    while True:
        page = adapter.page(offset=offset, limit=size, expected_collection=token)
        pages.append(page.model_dump())
        token = page.pagination.collection_token
        if page.pagination.next_offset is None: break
        offset = page.pagination.next_offset
    observations = collect_pages(pages)
    assert len(observations) == 504
    assert sum(o.value is None for o in observations) == 8


def test_route_pinning_errors_read_only_and_explicit_completeness():
    client = TestClient(create_app())
    path = '/api/v1/analytical/v1/mortality-trends'
    first = client.get(path,params={'limit':73})
    assert first.status_code == 200
    body = first.json(); token = body['pagination']['collection_token']
    assert body['pagination']['total'] == 504
    assert not body['pagination']['page_is_complete_collection']
    assert client.get(path,params={'offset':73}).status_code == 409
    assert client.get(path,params={'offset':73,'expected_collection':'0'*64}).status_code == 409
    second = client.get(path,params={'offset':73,'limit':73,'expected_collection':token})
    assert second.status_code == 200 and second.json()['pagination']['returned'] == 73
    for params in ({'limit':0},{'limit':1001},{'offset':-1},{'expected_collection':'bad'},{'geography_id':'fake'},{'offset':505,'expected_collection':token}):
        assert client.get(path,params=params).status_code == 422
    assert client.post(path,json={}).status_code == 405


def test_collector_rejects_partial_duplicate_corrupt_and_mixed_pages(adapter):
    first = adapter.page(limit=300).model_dump()
    second = adapter.page(offset=300,limit=300,expected_collection=first['pagination']['collection_token']).model_dump()
    for pages in ([first], [second,first], [first,first], []):
        with pytest.raises(CollectionConflict): collect_pages(pages)
    variants = []
    mixed = copy.deepcopy(second); mixed['artifact']['analytical_version'] += '-changed'; variants.append(mixed)
    mixed = copy.deepcopy(second); mixed['pagination']['collection_token'] = '0'*64; variants.append(mixed)
    mixed = copy.deepcopy(second); mixed['observations'][0]['value'] += 1; variants.append(mixed)
    mixed = copy.deepcopy(second); mixed['observations'][0]['observation_id'] = first['observations'][0]['observation_id']; variants.append(mixed)
    mixed = copy.deepcopy(second); mixed['pagination']['returned'] -= 1; variants.append(mixed)
    for variant in variants:
        with pytest.raises(CollectionConflict): collect_pages([first,variant])
    empty = copy.deepcopy(first)
    empty['observations'] = []
    empty['pagination'].update(returned=0, next_offset=0)
    with pytest.raises(CollectionConflict): collect_pages([empty, first, second])
    terminal = adapter.page(offset=504,expected_collection=first['pagination']['collection_token']).model_dump()
    with pytest.raises(CollectionConflict): collect_pages([first,second,terminal])


class ChangedRepository:
    def __init__(self, change): self.change = change
    def load(self, key):
        rows, meta = ArtifactRepository().load(key)
        rows, meta = copy.deepcopy(rows), copy.deepcopy(meta)
        self.change(rows,meta)
        return rows, meta


@pytest.mark.parametrize('field,value', [
    ('observed_value',-1), ('observed_value',1.5), ('observed_value',True),
    ('observed_value',None), ('quality_status','suppressed'), ('quarter',5),
    ('period','2017 Q2'), ('ordinal',0), ('period_start','2017-02-01'),
    ('period_end','20170331'), ('geography','Inverclyde'), ('unit','rate'),
    ('source_sha256','bad'), ('source_url','http://example.com'),
    ('source_path','../source.xlsx'), ('year','2017'),
])
def test_invalid_input_is_rejected_not_repaired(field,value):
    repository = ChangedRepository(lambda rows,meta:rows[0].__setitem__(field,value))
    with pytest.raises(ArtifactError): MortalityAdapter(repository).page()


def test_inconsistent_shared_metadata_duplicate_slots_and_missing_fields_rejected():
    def duplicate(rows,meta): rows.append(copy.deepcopy(rows[0]))
    def missing(rows,meta): rows[0].pop('publication_date')
    def invalid_meta(rows,meta): meta['artifact_sha256']='invalid'
    for change in (duplicate,missing,invalid_meta):
        with pytest.raises(ArtifactError): MortalityAdapter(ChangedRepository(change)).page()


def test_true_zero_is_preserved_and_vintage_boundary_definition_scope_identity(complete):
    def zero(rows,meta): rows[0]['observed_value']=0
    assert MortalityAdapter(ChangedRepository(zero)).page().observations[0].value == 0
    o = complete.observations[0]
    original = o.observation_id
    assert original == observation_identity(complete.source,complete.indicator,o.geography,o.period)
    for source,indicator,scope,period in (
        (complete.source.model_copy(update={'source_version':'0'*64}),complete.indicator,o.geography,o.period),
        (complete.source,complete.indicator.model_copy(update={'original_reporting_qualification':'Different definition'}),o.geography,o.period),
        (complete.source,complete.indicator,o.geography.model_copy(update={'boundary_type':'country'}),o.period),
        (complete.source,complete.indicator,o.geography,o.period.model_copy(update={'quarter':2})),
    ):
        assert observation_identity(source,indicator,scope,period) != original


def test_changed_collection_is_rejected_even_with_same_artifact_claim(adapter):
    token=adapter.page().pagination.collection_token
    changed=MortalityAdapter(ChangedRepository(lambda rows,meta: rows[0].__setitem__('observed_value',19)))
    with pytest.raises(CollectionConflict): changed.page(offset=100,expected_collection=token)


def test_existing_repository_checksum_validation_is_used(tmp_path):
    directory=tmp_path/'analysis/phase4/outputs';directory.mkdir(parents=True)
    for name in ('mortality_quarterly.csv','run_manifest.json'):
        (directory/name).write_bytes((ROOT/'analysis/phase4/outputs'/name).read_bytes())
    with (directory/'mortality_quarterly.csv').open('ab') as handle: handle.write(b'\n')
    with pytest.raises(ArtifactError): MortalityAdapter(ArtifactRepository(tmp_path)).page()


def test_invalid_contract_is_not_exposed_as_success():
    repository = ChangedRepository(lambda rows,meta:rows[0].__setitem__('observed_value',-1))
    client = TestClient(create_app(PlatformService(artifacts=repository)))
    response = client.get('/api/v1/analytical/v1/mortality-trends')
    assert response.status_code == 503
    assert response.json()['data'] == []
