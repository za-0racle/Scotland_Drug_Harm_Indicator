"""Additive, source-aware view of existing verified mortality artifacts.

No storage, imputation, aggregation, rate calculation or statistical fitting.
"""
from datetime import date, datetime
from urllib.parse import urlparse
from backend.repositories.artifacts import ArtifactError
from backend.services.analytical_integrity import fingerprint, relative_path
from backend.services.platform import geography
from backend.schemas.mortality_v1 import (
    CONTRACT_VERSION, SourceDefinition, IndicatorDefinition, ArtifactDefinition,
    ResearchMetadata, ResearchContext, Quarter, GeographyScope,
    MortalityObservation, MortalityPage, Pagination,
)

def observation_identity(source, indicator, scope, period):
    """Content/version scoped; value is deliberately not an identity dimension."""
    key = dict(contract_version=CONTRACT_VERSION, source_id=source.source_id,
               source_version=source.source_version, indicator=indicator.model_dump(),
               geography=scope.model_dump(), period=period.model_dump())
    return 'mortality-observation:v1:' + fingerprint(key)

class CollectionConflict(ValueError):
    pass


class MortalityAdapter:
    def __init__(self, artifacts):
        self.artifacts = artifacts

    def collection(self):
        try:
            rows, meta = self.artifacts.load('mortality_trends')
            if not rows:
                raise ValueError('Empty mortality artifact')
            artifact = ArtifactDefinition.model_validate(meta)
            if datetime.fromisoformat(artifact.executed_at_utc).tzinfo is None:
                raise ValueError('Artifact execution timestamp requires timezone')
            first = rows[0]
            source = SourceDefinition(
                source_id=first['source_id'], source_version=first['source_sha256'],
                source_path=first['source_path'], source_url=first['source_url'],
                publication_date=first['publication_date'], publication_status=first['publication_status'],
                source_data_cutoff=first['source_data_cutoff'])
            relative_path(source.source_path)
            if source.source_path.rsplit('/', 1)[-1] != source.source_id:
                raise ValueError('Source identifier/path mismatch')
            url = urlparse(source.source_url)
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError('Invalid source URL')
            for value in (source.publication_date, source.source_data_cutoff, first['analysis_as_of']):
                if value is not None and date.fromisoformat(value).isoformat() != value:
                    raise ValueError('Invalid source date')
            indicator = IndicatorDefinition(
                indicator_id=first['indicator_id'],
                definition='Police Scotland provisional originally suspected drug deaths; not NRS registered deaths or population-adjusted risk.',
                unit=first['unit'], period_basis=first['period_basis'],
                original_reporting_qualification=first['limitations'], scientific_status=first['scientific_status'],
                calculation_method=first['calculation_method'], year_comparison_basis=first['year_comparison_basis'],
                rolling_periods=first['rolling_periods'], reference_periods=first['reference_periods'])
            research = ResearchMetadata(analysis_as_of=first['analysis_as_of'], data_age_days=first['data_age_days'])
            shared_fields = {'source_id','source_sha256','source_path','source_url','publication_date','publication_status','source_data_cutoff',
                             'indicator_id','unit','period_basis','limitations','scientific_status','calculation_method','year_comparison_basis',
                             'rolling_periods','reference_periods','analysis_as_of','data_age_days'}
            per_row_fields = {'geography','period','ordinal','year','quarter','period_start','period_end','observed_value','quality_status'} | set(ResearchContext.model_fields)
            observations = []
            identities = set()
            last_period = {}
            for row in rows:
                if set(row) != shared_fields | per_row_fields or any(row[k] != first[k] or type(row[k]) != type(first[k]) for k in shared_fields):
                    raise ValueError('Unexpected schema or inconsistent shared metadata')
                raw_name = row['geography']
                g = geography(raw_name)
                scope = GeographyScope(geography_id=g['geography_id'], canonical_name=g['name'], original_name=raw_name, boundary_type=g['boundary_type'])
                period = Quarter(year=row['year'], quarter=row['quarter'], label=row['period'], ordinal=row['ordinal'],
                                 period_start=row['period_start'], period_end=row['period_end'])
                oid = observation_identity(source, indicator, scope, period)
                if oid in identities or period.ordinal <= last_period.get(scope.geography_id, -1):
                    raise ValueError('Duplicate identity or unordered quarterly history')
                identities.add(oid)
                last_period[scope.geography_id] = period.ordinal
                observations.append(MortalityObservation(observation_id=oid, geography=scope, period=period,
                    value=row['observed_value'], availability_status=row['quality_status'],
                    research_context=ResearchContext.model_validate({k:row[k] for k in ResearchContext.model_fields})))
            content = dict(contract_version=CONTRACT_VERSION, source=source.model_dump(), indicator=indicator.model_dump(),
                           artifact=artifact.model_dump(), research_metadata=research.model_dump(),
                           observations=[o.model_dump() for o in observations])
            return source, indicator, artifact, research, observations, fingerprint(content)
        except ArtifactError:
            raise
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            raise ArtifactError('Mortality analytical contract validation failed') from error

    def page(self, offset=0, limit=100, expected_collection=None):
        if type(offset) is not int or not 0 <= offset <= 1000000 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('Invalid pagination bounds')
        if offset and not expected_collection:
            raise CollectionConflict('Continuation requires expected_collection from the first page')
        source, indicator, artifact, research, observations, token = self.collection()
        if expected_collection is not None and expected_collection != token:
            raise CollectionConflict('Collection changed; discard collected pages and restart at offset zero')
        total = len(observations)
        if offset > total:
            raise ValueError('Offset exceeds collection total')
        selected = observations[offset:offset + limit]
        end = offset + len(selected)
        return MortalityPage(source=source, indicator=indicator, artifact=artifact, research_metadata=research,
                             observations=selected, pagination=Pagination(total=total, offset=offset, limit=limit,
                             returned=len(selected), next_offset=end if end < total else None,
                             page_is_complete_collection=offset == 0 and end == total, collection_token=token))


def collect_pages(pages):
    """Independently usable verifier: rejects gaps, overlaps and mixed versions.

    Existing frontend screens do not call this function or the new route.
    """
    records = []
    expected_offset = 0
    identity = None
    for raw in pages:
        page = MortalityPage.model_validate(raw)
        p = page.pagination
        current = fingerprint(dict(contract=page.contract_version, source=page.source.model_dump(),
            indicator=page.indicator.model_dump(), artifact=page.artifact.model_dump(), research=page.research_metadata.model_dump(),
            token=p.collection_token, total=p.total))
        if identity is not None and identity != current:
            raise CollectionConflict('Mixed-version page collection')
        if identity is not None and expected_offset >= p.total:
            raise CollectionConflict('Pages supplied after collection completion')
        identity = current
        if (p.offset != expected_offset or p.returned != len(page.observations)
                or p.returned > p.limit or p.returned == 0 and p.total > 0):
            raise CollectionConflict('Gapped or overlapping page collection')
        records.extend(page.observations)
        expected_offset += p.returned
        if expected_offset > p.total or p.next_offset != (expected_offset if expected_offset < p.total else None):
            raise CollectionConflict('Inconsistent pagination completeness')
        if p.page_is_complete_collection != (p.offset == 0 and expected_offset == p.total):
            raise CollectionConflict('Inconsistent complete-collection flag')
    if identity is None or expected_offset != p.total:
        raise CollectionConflict('Incomplete page collection')
    if len({r.observation_id for r in records}) != len(records):
        raise CollectionConflict('Duplicate observation identities')
    for row in records:
        if row.observation_id != observation_identity(page.source, page.indicator, row.geography, row.period):
            raise CollectionConflict('Invalid observation identity')
    content = dict(contract_version=page.contract_version, source=page.source.model_dump(), indicator=page.indicator.model_dump(),
                   artifact=page.artifact.model_dump(), research_metadata=page.research_metadata.model_dump(),
                   observations=[r.model_dump() for r in records])
    if fingerprint(content) != p.collection_token:
        raise CollectionConflict('Collection fingerprint mismatch')
    return records
