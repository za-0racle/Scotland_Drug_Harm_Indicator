"""Task 08E: compare the new contract with immutable Task 08B evidence."""
import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.config import ROOT
from backend.main import create_app
from backend.repositories.artifacts import ArtifactRepository, ArtifactError
from backend.schemas.forensic_v1 import ForensicObservation, ForensicPage
from backend.services.analytical_integrity import fingerprint
from backend.services.forensic_adapter import (
    ForensicAdapter,
    ForensicCollectionConflict,
    collect_forensic_pages,
    observation_identity,
)
BASELINE_08B = ROOT / 'docs/baselines/task08b'
BASELINE_08E = ROOT / 'docs/baselines/task08e/forensic-baseline.json'
ROUTE = '/api/v1/analytical/v1/forensic-toxicology'
NUMERIC_FIELDS = {
    'observed_value', 'count', 'rate', 'lower95', 'upper95', 'total_deaths',
    'prediction', 'forecast', 'statistic_value', 'lower_limit', 'upper_limit', 'suspected_deaths',
}


def load_evidence(path):
    return json.loads(path.read_text(encoding='utf-8'))


def forensic_baseline():
    return load_evidence(BASELINE_08E)


def task08b_resource():
    return next(row for row in load_evidence(BASELINE_08B / 'resource-contracts.json')
                if row['resource'] == 'forensic')


def legacy_record(page, observation):
    source, measure, research = page.source, page.measure, page.research_metadata
    context, period, geo = observation.research_context, observation.period, observation.geography
    return dict(
        indicator_id=observation.indicator_id,
        source_id=source.source_id,
        source_path=source.source_path,
        geography=geo.original_name,
        period=period.label,
        ordinal=period.ordinal,
        observed_value=observation.value,
        unit=measure.unit,
        period_basis=measure.period_basis,
        period_start=period.period_start,
        period_end=period.period_end,
        quality_status=observation.availability_status,
        limitations=observation.limitations,
        previous_value=context.previous_value,
        period_change=context.period_change,
        period_change_pct=context.period_change_pct,
        year_reference_value=context.year_reference_value,
        year_change_pct=context.year_change_pct,
        rolling_average=context.rolling_average,
        rolling_periods=context.rolling_periods,
        historical_reference_mean=context.historical_reference_mean,
        reference_periods=context.reference_periods,
        reference_change_pct=context.reference_change_pct,
        direction=context.direction,
        percentage_point_change=context.percentage_point_change,
        year_comparison_basis=measure.year_comparison_basis,
        calculation_method=measure.calculation_method,
        comparison_status=context.comparison_status,
        within_source_period_dense_rank=context.within_source_period_dense_rank,
        source_sha256=source.source_version,
        source_url=source.source_url,
        publication_date=source.publication_date,
        source_data_cutoff=source.source_data_cutoff,
        analysis_as_of=research.analysis_as_of,
        data_age_days=research.data_age_days,
        publication_lag_days=context.publication_lag_days,
        publication_status=source.publication_status,
        scientific_status=measure.scientific_status,
        geography_id=geo.geography_id,
        name=geo.canonical_name,
        boundary_type=geo.boundary_type,
        source_geography=geo.original_name,
    )


@pytest.fixture(scope='module')
def adapter():
    return ForensicAdapter(ArtifactRepository())


@pytest.fixture(scope='module')
def complete(adapter):
    return adapter.page(limit=1000)


def test_forensic_baseline_matches_task08b_source_artifact_and_api(complete):
    baseline = forensic_baseline()
    old = task08b_resource()
    assert baseline['task08b_comparisons'] and all(baseline['task08b_comparisons'].values())
    assert len(baseline['manifest_checks']) == 85
    assert all(check['match'] for check in baseline['manifest_checks'])
    assert len(complete.observations) == old['artifact_records'] == old['api_records'] == 210
    records = [legacy_record(complete, observation) for observation in complete.observations]
    assert fingerprint(records) == old['ordered_response_fingerprint']
    assert fingerprint(records) == baseline['ordered_response_fingerprint']
    assert sorted(records[0]) == old['fields']
    numeric = [
        {key: row[key] for key in sorted(row)
         if key in NUMERIC_FIELDS or isinstance(row[key], (int, float)) and not isinstance(row[key], bool)}
        for row in records
    ]
    assert fingerprint(numeric) == old['numeric_field_projection_fingerprint']
    assert fingerprint(numeric) == baseline['numeric_fingerprint']
    assert complete.artifact.artifact_sha256 == old['metadata']['artifact_sha256']
    assert complete.source.source_version == baseline['source_sha256']
    assert sum(observation.value is None for observation in complete.observations) == baseline['observed_nulls'] == 0
    assert sum(observation.value == 0 for observation in complete.observations) == baseline['observed_zeros'] == 1
    assert len({observation.period.ordinal for observation in complete.observations}) == baseline['quarters'] == 30


def test_raw_source_and_phase4_artifact_are_lossless_and_source_defined(complete):
    baseline = forensic_baseline()
    old_files = load_evidence(BASELINE_08B / 'file-inventory.json')
    source_file = ROOT / 'datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv'
    artifact_file = ROOT / 'analysis/phase4/outputs/forensic_counts.csv'
    with source_file.open(encoding='utf-8-sig', newline='') as handle:
        source_rows = list(csv.DictReader(handle))
    with artifact_file.open(encoding='utf-8', newline='') as handle:
        artifact_rows = list(csv.DictReader(handle))
    source_evidence = next(row for row in old_files if row['path'] == complete.source.source_path)
    artifact_evidence = next(row for row in old_files if row['path'] == complete.artifact.source_path)
    assert source_rows == baseline['raw_source_records']
    assert fingerprint(source_rows) == source_evidence['ordered_record_fingerprint']
    assert fingerprint(artifact_rows) == artifact_evidence['ordered_record_fingerprint']
    assert len(source_rows) == len(artifact_rows) == 210
    assert sorted(category.original_label for category in complete.categories) == baseline['categories']
    assert {row['measure'] for row in source_rows} == set(baseline['original_measure']) == {'Number'}
    assert {observation.period.original_label for observation in complete.observations} == {
        row['Quarter'] for row in source_rows
    }
    assert all(category.source_definition is None for category in complete.categories)
    assert all(category.definition_status == 'source_label_only' and not category.additive
               for category in complete.categories)
    assert complete.measure.sample_or_testing_definition is None
    assert complete.measure.sample_definition_status == 'not_provided_by_source'
    assert complete.measure.sample_denominator is None
    assert complete.source.publication_date is None
    assert all(observation.availability_status == 'observed' for observation in complete.observations)


def test_new_route_pins_pages_and_preserves_existing_forensic_and_mortality_api():
    client = TestClient(create_app())
    first = client.get(ROUTE, params={'limit': 73})
    assert first.status_code == 200
    first_body = first.json()
    token = first_body['pagination']['collection_token']
    assert first_body['contract_version'] == 'forensic-toxicology/1.0.0'
    assert first_body['pagination']['total'] == 210
    assert first_body['pagination']['next_offset'] == 73
    assert not first_body['pagination']['page_is_complete_collection']
    assert client.get(ROUTE, params={'offset': 73}).status_code == 409
    assert client.get(ROUTE, params={'offset': 73, 'expected_collection': '0' * 64}).status_code == 409
    following = client.get(ROUTE, params={'offset': 73, 'limit': 73, 'expected_collection': token})
    assert following.status_code == 200
    assert following.json()['pagination']['returned'] == 73
    assert following.json()['pagination']['collection_token'] == token
    for params in (
        {'limit': 0}, {'limit': 1001}, {'offset': -1}, {'offset': 211, 'expected_collection': token},
        {'expected_collection': 'bad'}, {'category': 'benzodiazepines'},
    ):
        assert client.get(ROUTE, params=params).status_code == 422
    assert client.post(ROUTE, json={}).status_code == 405

    baseline = task08b_resource()
    old = client.get('/api/v1/toxicology/forensic', params={'limit': 1000}).json()
    assert old['total'] == 210
    assert fingerprint(old['data']) == baseline['ordered_response_fingerprint']
    previous_openapi = load_evidence(ROOT / 'docs/baselines/task08e/openapi-before.json')
    current_openapi = client.get('/openapi.json').json()
    for path, definition in previous_openapi['paths'].items():
        assert current_openapi['paths'][path] == definition
    assert set(current_openapi['paths']) - set(previous_openapi['paths']) == {
        ROUTE,
        '/api/v1/database/v1/data-sources',
        '/api/v1/database/v1/geographic-areas',
        '/api/v1/database/v1/naloxone-activity',
        '/api/v1/forecasting/generate',
        '/api/v1/forecasting/options',
    }


def test_deterministic_identity_and_null_zero_availability(complete):
    observation = complete.observations[0]
    category = next(item for item in complete.categories if item.category_id == observation.category_id)
    assert observation.observation_id == observation_identity(
        complete.source, complete.artifact, complete.measure, category,
        observation.geography, observation.period, observation.indicator_id,
    )
    assert observation.value == 42
    assert any(item.value == 0 and item.availability_status == 'observed' for item in complete.observations)

    missing = observation.model_dump()
    missing.update(value=None, availability_status='missing_or_suppressed')
    assert ForensicObservation.model_validate(missing).value is None
    missing['availability_status'] = 'observed'
    with pytest.raises(ValidationError):
        ForensicObservation.model_validate(missing)
    invalid_value = observation.model_dump()
    invalid_value['research_context']['rolling_average'] = float('inf')
    with pytest.raises(ValidationError):
        ForensicObservation.model_validate(invalid_value)
    changed = observation.period.model_copy(update={'quarter': 1})
    assert observation_identity(
        complete.source, complete.artifact, complete.measure, category,
        observation.geography, changed, observation.indicator_id,
    ) != observation.observation_id


def test_complete_collection_verifier_rejects_gaps_duplicates_and_mixed_pages(adapter):
    pages = []
    offset = 0
    token = None
    while True:
        page = adapter.page(offset=offset, limit=73, expected_collection=token)
        pages.append(page.model_dump())
        token = page.pagination.collection_token
        if page.pagination.next_offset is None:
            break
        offset = page.pagination.next_offset
    assert len(collect_forensic_pages(pages)) == 210
    for broken in ([pages[0]], [pages[1], pages[0]], [pages[0], pages[0]], []):
        with pytest.raises(ForensicCollectionConflict):
            collect_forensic_pages(broken)
    mixed = copy.deepcopy(pages[1])
    mixed['observations'][0]['value'] += 1
    with pytest.raises(ForensicCollectionConflict):
        collect_forensic_pages([pages[0], mixed, pages[2]])
    duplicate = copy.deepcopy(pages[1])
    duplicate['observations'][0]['observation_id'] = pages[0]['observations'][0]['observation_id']
    with pytest.raises(ForensicCollectionConflict):
        collect_forensic_pages([pages[0], duplicate, pages[2]])


class ChangedRepository:
    def __init__(self, change):
        self.root = ROOT
        self.change = change

    def load(self, key):
        rows, metadata = ArtifactRepository().load(key)
        rows, metadata = copy.deepcopy(rows), copy.deepcopy(metadata)
        self.change(rows, metadata)
        return rows, metadata


@pytest.mark.parametrize('change', [
    lambda rows, _metadata: rows[0].__setitem__('observed_value', rows[0]['observed_value'] + 1),
    lambda rows, _metadata: rows[0].__setitem__('indicator_id', 'forensic:Other'),
    lambda rows, _metadata: rows[0].__setitem__('unit', 'count'),
    lambda rows, _metadata: rows[0].__setitem__('period', '2018 Q5'),
    lambda rows, _metadata: rows[0].__setitem__('source_sha256', '0' * 64),
    lambda rows, _metadata: rows[0].__setitem__('source_url', 'http://example.test/'),
    lambda rows, _metadata: rows[0].__setitem__('rolling_average', float('inf')),
    lambda rows, _metadata: rows[0].pop('observed_value'),
    lambda rows, _metadata: rows.append(copy.deepcopy(rows[0])),
    lambda _rows, metadata: metadata.__setitem__('artifact_sha256', '0' * 64),
])
def test_invalid_artifact_identity_values_and_duplicate_keys_fail_closed(change):
    with pytest.raises(ArtifactError):
        ForensicAdapter(ChangedRepository(change)).page()


def test_missing_category_definitions_and_invalid_quarters_are_rejected(complete):
    body = complete.model_dump()
    body['categories'].pop()
    with pytest.raises(ValidationError):
        ForensicPage.model_validate(body)
    body = complete.model_dump()
    body['contract_version'] = 'forensic-toxicology/2.0.0'
    with pytest.raises(ValidationError):
        ForensicPage.model_validate(body)
    body = complete.model_dump()
    body['observations'][0]['period']['original_label'] = 'Q3 2018'
    with pytest.raises(ValidationError):
        ForensicPage.model_validate(body)


def test_all_85_source_manifest_checks_still_match():
    checks = load_evidence(BASELINE_08B / 'manifest-verification.json')
    assert len(checks) == 85
    for check in checks:
        path = ROOT / Path(*Path(check['manifest']).parent.parts) / check['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == check['expected'], path
