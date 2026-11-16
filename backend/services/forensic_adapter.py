"""Versioned, source-specific view of the existing Phase 4 forensic artifact."""
import csv
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from backend.repositories.artifacts import ArtifactError
from backend.services.analytical_integrity import fingerprint, relative_path
from backend.schemas.forensic_v1 import (
    ARTIFACT_PATH,
    CATEGORY_LABELS,
    CONTRACT_VERSION,
    MANIFEST_PATH,
    SOURCE_ID,
    SOURCE_PATH,
    ArtifactDefinition,
    CategoryDefinition,
    ForensicObservation,
    ForensicPage,
    GeographyScope,
    MeasureDefinition,
    Pagination,
    ReportingQuarter,
    ResearchContext,
    ResearchMetadata,
    SourceDefinition,
)
from backend.services.platform import geography


class ForensicCollectionConflict(ValueError):
    pass


ARTIFACT_FIELDS = {
    'indicator_id', 'source_id', 'source_path', 'geography', 'period', 'ordinal', 'observed_value',
    'unit', 'period_basis', 'period_start', 'period_end', 'quality_status', 'limitations',
    'previous_value', 'period_change', 'period_change_pct', 'year_reference_value', 'year_change_pct',
    'rolling_average', 'rolling_periods', 'historical_reference_mean', 'reference_periods',
    'reference_change_pct', 'direction', 'percentage_point_change', 'year_comparison_basis',
    'calculation_method', 'comparison_status', 'within_source_period_dense_rank', 'source_sha256',
    'source_url', 'publication_date', 'source_data_cutoff', 'analysis_as_of', 'data_age_days',
    'publication_lag_days', 'publication_status', 'scientific_status',
}
RAW_FIELDS = {'Quarter', 'drug_name', 'measure', 'value'}
EXPECTED_OBSERVATIONS = 210
EXPECTED_QUARTERS = 30
SHARED_ARTIFACT_FIELDS = {
    'source_id', 'source_path', 'geography', 'unit', 'period_basis', 'limitations', 'rolling_periods',
    'reference_periods', 'year_comparison_basis', 'calculation_method', 'source_sha256', 'source_url',
    'publication_date', 'source_data_cutoff', 'analysis_as_of', 'data_age_days', 'publication_lag_days',
    'publication_status', 'scientific_status',
}


def category_identity(source, label):
    return 'forensic-category:v1:' + fingerprint({
        'contract_version': CONTRACT_VERSION,
        'source_id': source.source_id,
        'source_version': source.source_version,
        'original_label': label,
    })


def observation_identity(source, artifact, measure, category, geography_scope, period, indicator_id):
    return 'forensic-observation:v1:' + fingerprint({
        'contract_version': CONTRACT_VERSION,
        'source': source.model_dump(),
        'artifact': dict(analytical_version=artifact.analytical_version, artifact_sha256=artifact.artifact_sha256),
        'measure': measure.model_dump(),
        'category': category.model_dump(),
        'indicator_id': indicator_id,
        'geography': geography_scope.model_dump(),
        'period': period.model_dump(),
    })


class ForensicAdapter:
    def __init__(self, artifacts):
        self.artifacts = artifacts

    def collection(self):
        try:
            rows, metadata = self.artifacts.load('forensic')
            if not rows:
                raise ValueError('Empty forensic artifact')
            if set(rows[0]) != ARTIFACT_FIELDS or any(set(row) != ARTIFACT_FIELDS for row in rows):
                raise ValueError('Unexpected forensic artifact schema')
            artifact = ArtifactDefinition.model_validate(metadata)
            executed = datetime.fromisoformat(artifact.executed_at_utc)
            if executed.tzinfo is None:
                raise ValueError('Forensic artifact execution timestamp requires timezone')

            first = rows[0]
            if (len(rows) != EXPECTED_OBSERVATIONS
                    or first['source_id'] != SOURCE_ID or first['source_path'] != SOURCE_PATH):
                raise ValueError('Invalid forensic source identity or observation count')
            relative_path(first['source_path'])
            manifest_path = relative_path(artifact.provenance_manifest)
            manifest = json.loads((self.artifacts.root / Path(*manifest_path.split('/'))).read_text(encoding='utf-8'))
            source_entry = manifest['sources'][SOURCE_PATH]
            source_file = self.artifacts.root / Path(*SOURCE_PATH.split('/'))
            source_sha = hashlib.sha256(source_file.read_bytes()).hexdigest()
            artifact_file = self.artifacts.root / Path(*ARTIFACT_PATH.split('/'))
            artifact_sha = hashlib.sha256(artifact_file.read_bytes()).hexdigest()
            if (artifact.provenance_manifest != MANIFEST_PATH
                    or artifact.source_path != ARTIFACT_PATH
                    or source_sha != first['source_sha256'] or source_sha != source_entry['sha256']
                    or artifact_sha != artifact.artifact_sha256
                    or artifact_sha != manifest['output_hashes']['forensic_counts.csv']
                    or manifest.get('version') != artifact.analytical_version
                    or manifest.get('executed_at_utc') != artifact.executed_at_utc
                    or source_entry.get('publisher') != 'Public Health Scotland'
                    or source_entry.get('url') != first['source_url']):
                raise ValueError('Forensic source or artifact provenance mismatch')
            source_url = source_entry['url']
            parsed_url = urlparse(source_url)
            if parsed_url.scheme != 'https' or not parsed_url.hostname or parsed_url.username or parsed_url.password:
                raise ValueError('Invalid forensic source URL')
            source = SourceDefinition(
                source_id=SOURCE_ID,
                source_version=source_sha,
                source_path=SOURCE_PATH,
                source_url=source_url,
                publisher=source_entry['publisher'],
                publication_date=first['publication_date'],
                publication_status=first['publication_status'],
                source_data_cutoff=first['source_data_cutoff'],
            )
            if date.fromisoformat(source.source_data_cutoff).isoformat() != source.source_data_cutoff:
                raise ValueError('Invalid forensic source cutoff date')

            raw_path = self.artifacts.root / Path(*SOURCE_PATH.split('/'))
            with raw_path.open(encoding='utf-8-sig', newline='') as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None or set(reader.fieldnames) != RAW_FIELDS:
                    raise ValueError('Unexpected forensic source fields')
                raw_rows = list(reader)
            if len(raw_rows) != len(rows):
                raise ValueError('Incomplete forensic source/artifact collection')

            labels = list(dict.fromkeys(raw['drug_name'] for raw in raw_rows))
            if tuple(labels) != CATEGORY_LABELS:
                raise ValueError('Missing or unsupported source-defined forensic categories')
            raw_by_key = {}
            source_periods = set()
            for raw in raw_rows:
                match = re.fullmatch(r'Q([1-4]) (\d{4})', raw['Quarter'])
                if match is None:
                    raise ValueError('Invalid original forensic reporting quarter')
                quarter, year = map(int, match.groups())
                ordinal = year * 4 + quarter - 1
                key = (raw['drug_name'], ordinal)
                if key in raw_by_key:
                    raise ValueError('Duplicate source forensic category and reporting quarter')
                raw_by_key[key] = raw
                source_periods.add(ordinal)
            expected_periods = sorted(source_periods)
            if len(expected_periods) != EXPECTED_QUARTERS or set(raw_by_key) != {
                    (label, ordinal) for label in CATEGORY_LABELS for ordinal in expected_periods}:
                raise ValueError('Incomplete source forensic category history')
            categories = [
                CategoryDefinition(
                    category_id=category_identity(source, label),
                    original_label=label,
                    source_definition=None,
                    definition_status='source_label_only',
                    relationship='overlapping_source_groups',
                    additive=False,
                )
                for label in labels
            ]
            category_by_label = {category.original_label: category for category in categories}
            measure = MeasureDefinition(
                definition='Source-reported Number of forensic toxicology detections by original category and calendar quarter; categories overlap and do not represent unique deaths or people.',
                source_measure='Number',
                unit='detection_count',
                period_basis='calendar_quarter',
                calculation_method=first['calculation_method'],
                year_comparison_basis=first['year_comparison_basis'],
                rolling_periods=first['rolling_periods'],
                reference_periods=first['reference_periods'],
                scientific_status=first['scientific_status'],
                sample_or_testing_definition=None,
                sample_definition_status='not_provided_by_source',
                sample_denominator=None,
            )
            research = ResearchMetadata(
                analysis_as_of=first['analysis_as_of'],
                data_age_days=first['data_age_days'],
            )

            observations = []
            seen = set()
            category_periods = {label: [] for label in CATEGORY_LABELS}
            for row in rows:
                if any(row[key] != first[key] or type(row[key]) is not type(first[key])
                       for key in SHARED_ARTIFACT_FIELDS):
                    raise ValueError('Inconsistent forensic artifact metadata')
                if not row['indicator_id'].startswith('forensic:'):
                    raise ValueError('Invalid forensic indicator identity')
                label = row['indicator_id'][len('forensic:'):]
                match = re.fullmatch(r'(\d{4}) Q([1-4])', row['period'])
                if match is None:
                    raise ValueError('Invalid analytical forensic reporting quarter')
                year, quarter = map(int, match.groups())
                ordinal = year * 4 + quarter - 1
                raw = raw_by_key.get((label, ordinal))
                if raw is None:
                    raise ValueError('Analytical forensic row has no matching source observation')
                if raw['measure'] != 'Number' or not re.fullmatch(r'\d+', raw['value']):
                    raise ValueError('Invalid source forensic measure or value')
                if (row['indicator_id'] != f"forensic:{raw['drug_name']}"
                        or row['unit'] != measure.unit or row['period_basis'] != measure.period_basis
                        or row['source_url'] != source.source_url or row['source_sha256'] != source.source_version
                        or row['geography'] != 'Scotland forensic testing sample'
                        or row['observed_value'] != int(raw['value'])
                        or type(row['observed_value']) is not int
                        or row['quality_status'] != 'observed'):
                    raise ValueError('Forensic source and analytical artifact disagree')
                period = ReportingQuarter(
                    year=year,
                    quarter=quarter,
                    label=row['period'],
                    original_label=raw['Quarter'],
                    ordinal=row['ordinal'],
                    period_start=row['period_start'],
                    period_end=row['period_end'],
                )
                if row['ordinal'] != year * 4 + quarter - 1:
                    raise ValueError('Forensic reporting order disagrees with source quarter')
                category = category_by_label[raw['drug_name']]
                key = (category.category_id, period.ordinal)
                if key in seen:
                    raise ValueError('Duplicate forensic source category and reporting quarter')
                seen.add(key)
                category_periods[raw['drug_name']].append(period.ordinal)

                geo = geography('Scotland forensic testing sample', 'national_testing_sample')
                scope = GeographyScope(
                    geography_id=geo['geography_id'],
                    canonical_name='Scotland forensic testing sample',
                    original_name='Scotland forensic testing sample',
                    boundary_type='national_testing_sample',
                )
                context = ResearchContext(
                    previous_value=row['previous_value'],
                    period_change=row['period_change'],
                    period_change_pct=row['period_change_pct'],
                    year_reference_value=row['year_reference_value'],
                    year_change_pct=row['year_change_pct'],
                    rolling_average=row['rolling_average'],
                    rolling_periods=row['rolling_periods'],
                    historical_reference_mean=row['historical_reference_mean'],
                    reference_periods=row['reference_periods'],
                    reference_change_pct=row['reference_change_pct'],
                    direction=row['direction'],
                    percentage_point_change=row['percentage_point_change'],
                    comparison_status=row['comparison_status'],
                    within_source_period_dense_rank=row['within_source_period_dense_rank'],
                    publication_lag_days=row['publication_lag_days'],
                )
                indicator_id = row['indicator_id']
                identity = observation_identity(source, artifact, measure, category, scope, period, indicator_id)
                observation = ForensicObservation(
                    observation_id=identity,
                    indicator_id=indicator_id,
                    category_id=category.category_id,
                    geography=scope,
                    period=period,
                    value=row['observed_value'],
                    availability_status=row['quality_status'],
                    limitations=row['limitations'],
                    research_context=context,
                )
                observations.append(observation)
            if (seen != {(category_by_label[label].category_id, ordinal)
                          for label in CATEGORY_LABELS for ordinal in expected_periods}
                    or any(values != expected_periods for values in category_periods.values())):
                raise ValueError('Incomplete or unordered forensic category history')
            content = dict(
                contract_version=CONTRACT_VERSION,
                source=source.model_dump(),
                artifact=artifact.model_dump(),
                measure=measure.model_dump(),
                categories=[category.model_dump() for category in categories],
                research_metadata=research.model_dump(),
                observations=[observation.model_dump() for observation in observations],
            )
            return source, artifact, measure, categories, research, observations, fingerprint(content)
        except ArtifactError:
            raise
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            raise ArtifactError('Forensic analytical contract validation failed') from error

    def page(self, offset=0, limit=100, expected_collection=None):
        if (type(offset) is not int or not 0 <= offset <= 1000000
                or type(limit) is not int or not 1 <= limit <= 1000):
            raise ValueError('Invalid forensic pagination bounds')
        if expected_collection is not None and not re.fullmatch(r'[0-9a-f]{64}', expected_collection):
            raise ValueError('Invalid forensic collection token')
        if offset and not expected_collection:
            raise ForensicCollectionConflict('Continuation requires expected_collection from the first page')
        source, artifact, measure, categories, research, observations, token = self.collection()
        if expected_collection is not None and expected_collection != token:
            raise ForensicCollectionConflict('Collection changed; discard pages and restart at offset zero')
        if offset > len(observations):
            raise ValueError('Offset exceeds forensic collection total')
        selected = observations[offset:offset + limit]
        end = offset + len(selected)
        return ForensicPage(
            source=source,
            artifact=artifact,
            measure=measure,
            categories=categories,
            research_metadata=research,
            observations=selected,
            pagination=Pagination(
                total=len(observations),
                offset=offset,
                limit=limit,
                returned=len(selected),
                next_offset=end if end < len(observations) else None,
                page_is_complete_collection=offset == 0 and end == len(observations),
                collection_token=token,
            ),
        )


def collect_forensic_pages(pages):
    """Reject gaps, overlaps, mixed versions, and incomplete forensic collections."""
    records = []
    expected_offset = 0
    identity = None
    page = None
    for raw in pages:
        page = ForensicPage.model_validate(raw)
        p = page.pagination
        current = fingerprint(dict(
            contract=page.contract_version,
            source=page.source.model_dump(),
            artifact=page.artifact.model_dump(),
            measure=page.measure.model_dump(),
            categories=[category.model_dump() for category in page.categories],
            research=page.research_metadata.model_dump(),
            token=p.collection_token,
            total=p.total,
        ))
        if identity is not None and identity != current:
            raise ForensicCollectionConflict('Mixed-version forensic page collection')
        if identity is not None and expected_offset >= p.total:
            raise ForensicCollectionConflict('Pages supplied after forensic collection completion')
        identity = current
        if (p.offset != expected_offset or p.returned != len(page.observations)
                or p.returned > p.limit or p.returned == 0 and p.total > 0):
            raise ForensicCollectionConflict('Gapped or overlapping forensic page collection')
        records.extend(page.observations)
        expected_offset += p.returned
        if expected_offset > p.total or p.next_offset != (expected_offset if expected_offset < p.total else None):
            raise ForensicCollectionConflict('Inconsistent forensic pagination completeness')
        if p.page_is_complete_collection != (p.offset == 0 and expected_offset == p.total):
            raise ForensicCollectionConflict('Inconsistent forensic complete-collection flag')
    if page is None or expected_offset != page.pagination.total:
        raise ForensicCollectionConflict('Incomplete forensic page collection')
    if len({record.observation_id for record in records}) != len(records):
        raise ForensicCollectionConflict('Duplicate forensic observation identities')
    categories = {category.category_id: category for category in page.categories}
    if any(category.category_id != category_identity(page.source, category.original_label)
           for category in page.categories):
        raise ForensicCollectionConflict('Invalid forensic category identity')
    periods_by_category = {category_id: set() for category_id in categories}
    for record in records:
        category = categories[record.category_id]
        periods_by_category[record.category_id].add(record.period.ordinal)
        if record.observation_id != observation_identity(
                page.source, page.artifact, page.measure, category, record.geography, record.period, record.indicator_id):
            raise ForensicCollectionConflict('Invalid forensic observation identity')
    all_periods = set().union(*periods_by_category.values())
    if (len(records) != EXPECTED_OBSERVATIONS or len(all_periods) != EXPECTED_QUARTERS
            or any(periods != all_periods for periods in periods_by_category.values())):
        raise ForensicCollectionConflict('Incomplete forensic category-quarter collection')
    content = dict(
        contract_version=page.contract_version,
        source=page.source.model_dump(),
        artifact=page.artifact.model_dump(),
        measure=page.measure.model_dump(),
        categories=[category.model_dump() for category in page.categories],
        research_metadata=page.research_metadata.model_dump(),
        observations=[record.model_dump() for record in records],
    )
    if fingerprint(content) != page.pagination.collection_token:
        raise ForensicCollectionConflict('Forensic collection fingerprint mismatch')
    return records
