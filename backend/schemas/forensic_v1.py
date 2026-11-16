"""Strict, source-specific contract for Phase 4 forensic toxicology."""
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

CONTRACT_VERSION = 'forensic-toxicology/1.0.0'
SOURCE_ID = 'radar_toxicology_forensic_2018-2026.csv'
SOURCE_PATH = 'datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv'
ARTIFACT_PATH = 'analysis/phase4/outputs/forensic_counts.csv'
MANIFEST_PATH = 'analysis/phase4/outputs/run_manifest.json'
CATEGORY_LABELS = (
    'Opioids',
    'Prescribable Benzodiazepines',
    'Street Benzodiazepines',
    'All Benzodiazepines',
    'Dissociatives',
    'Gabapentinoids',
    'Stimulants',
)

Text = Annotated[str, StringConstraints(min_length=1, pattern=r'\S')]
SHA256 = Annotated[str, StringConstraints(pattern=r'^[0-9a-f]{64}$')]
Count = Annotated[int, Field(ge=0, strict=True)]
FiniteNumber = Annotated[int | float, Field(allow_inf_nan=False)]


class StrictRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', allow_inf_nan=False)


class SourceDefinition(StrictRecord):
    source_id: Literal['radar_toxicology_forensic_2018-2026.csv']
    source_version: SHA256
    source_path: Literal['datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv']
    source_url: Text
    publisher: Literal['Public Health Scotland']
    publication_date: None
    publication_status: Literal['unknown_publication_date']
    source_data_cutoff: Text


class ArtifactDefinition(StrictRecord):
    resource: Literal['forensic']
    analytical_version: Text
    artifact_sha256: SHA256
    source_path: Literal['analysis/phase4/outputs/forensic_counts.csv']
    provenance_manifest: Literal['analysis/phase4/outputs/run_manifest.json']
    storage: Literal['approved_local_artifact']
    executed_at_utc: Text
    limitations: list[Text]


class MeasureDefinition(StrictRecord):
    definition: Literal[
        'Source-reported Number of forensic toxicology detections by original category and calendar quarter; categories overlap and do not represent unique deaths or people.'
    ]
    source_measure: Literal['Number']
    unit: Literal['detection_count']
    period_basis: Literal['calendar_quarter']
    calculation_method: Text
    year_comparison_basis: Literal['same_calendar_period_previous_year']
    rolling_periods: Annotated[int, Field(gt=0, strict=True)]
    reference_periods: Annotated[int, Field(gt=0, strict=True)]
    scientific_status: Literal['descriptive_research_only_not_anomaly_or_alert']
    sample_or_testing_definition: None
    sample_definition_status: Literal['not_provided_by_source']
    sample_denominator: None


class CategoryDefinition(StrictRecord):
    category_id: Annotated[str, StringConstraints(pattern=r'^forensic-category:v1:[0-9a-f]{64}$')]
    original_label: Text
    source_definition: None
    definition_status: Literal['source_label_only']
    relationship: Literal['overlapping_source_groups']
    additive: Literal[False]


class ResearchMetadata(StrictRecord):
    analysis_as_of: Text
    data_age_days: Count


class GeographyScope(StrictRecord):
    geography_id: Text
    canonical_name: Literal['Scotland forensic testing sample']
    original_name: Literal['Scotland forensic testing sample']
    boundary_type: Literal['national_testing_sample']


class ReportingQuarter(StrictRecord):
    year: Annotated[int, Field(ge=1900, le=2100, strict=True)]
    quarter: Annotated[int, Field(ge=1, le=4, strict=True)]
    label: Text
    original_label: Text
    ordinal: Annotated[int, Field(strict=True)]
    period_start: Text
    period_end: Text

    @model_validator(mode='after')
    def exact_quarter(self):
        if (self.label != f'{self.year} Q{self.quarter}'
                or self.original_label != f'Q{self.quarter} {self.year}'
                or self.ordinal != self.year * 4 + self.quarter - 1):
            raise ValueError('Inconsistent forensic quarter label or ordering')
        start = date(self.year, self.quarter * 3 - 2, 1)
        end = date(self.year + 1, 1, 1) if self.quarter == 4 else date(self.year, self.quarter * 3 + 1, 1)
        if (self.period_start != start.isoformat()
                or date.fromisoformat(self.period_end).isoformat() != self.period_end
                or date.fromisoformat(self.period_end).toordinal() != end.toordinal() - 1):
            raise ValueError('Inconsistent forensic quarter dates')
        return self


class ResearchContext(StrictRecord):
    """Frozen Phase 4 descriptive fields; the adapter does not recompute them."""
    previous_value: Count | None
    period_change: Annotated[int, Field(strict=True)] | None
    period_change_pct: FiniteNumber | None
    year_reference_value: Count | None
    year_change_pct: FiniteNumber | None
    rolling_average: FiniteNumber | None
    rolling_periods: Annotated[int, Field(gt=0, strict=True)]
    historical_reference_mean: FiniteNumber | None
    reference_periods: Annotated[int, Field(gt=0, strict=True)]
    reference_change_pct: FiniteNumber | None
    direction: Literal['unavailable', 'increase', 'decrease', 'unchanged']
    percentage_point_change: None
    comparison_status: Literal['missing_reference', 'zero_reference_pct_undefined', 'descriptive_only']
    within_source_period_dense_rank: Count | None
    publication_lag_days: None


class ForensicObservation(StrictRecord):
    observation_id: Annotated[str, StringConstraints(pattern=r'^forensic-observation:v1:[0-9a-f]{64}$')]
    indicator_id: Text
    category_id: Annotated[str, StringConstraints(pattern=r'^forensic-category:v1:[0-9a-f]{64}$')]
    geography: GeographyScope
    period: ReportingQuarter
    value: Count | None
    availability_status: Literal['observed', 'missing_or_suppressed']
    limitations: Text
    research_context: ResearchContext

    @model_validator(mode='after')
    def value_availability(self):
        if (self.value is None) != (self.availability_status == 'missing_or_suppressed'):
            raise ValueError('Availability and forensic value disagree')
        return self


class Pagination(StrictRecord):
    total: Count
    offset: Count
    limit: Annotated[int, Field(ge=1, le=1000, strict=True)]
    returned: Count
    next_offset: Count | None
    page_is_complete_collection: bool
    collection_token: SHA256
    ordering: Literal['original_artifact_row_order'] = 'original_artifact_row_order'


class ForensicPage(StrictRecord):
    contract_version: Literal['forensic-toxicology/1.0.0'] = CONTRACT_VERSION
    source: SourceDefinition
    artifact: ArtifactDefinition
    measure: MeasureDefinition
    categories: list[CategoryDefinition]
    research_metadata: ResearchMetadata
    pagination: Pagination
    observations: list[ForensicObservation]

    @model_validator(mode='after')
    def collection_shape(self):
        p = self.pagination
        labels = [category.original_label for category in self.categories]
        if (labels != list(CATEGORY_LABELS)
                or len({category.category_id for category in self.categories}) != len(self.categories)):
            raise ValueError('Missing, duplicate, or unsupported forensic category definition')
        category_ids = {category.category_id for category in self.categories}
        if (p.returned != len(self.observations) or p.offset + p.returned > p.total
                or p.returned > p.limit
                or p.next_offset != (p.offset + p.returned if p.offset + p.returned < p.total else None)
                or p.page_is_complete_collection != (p.offset == 0 and p.returned == p.total)):
            raise ValueError('Inconsistent forensic pagination completeness')
        seen = set()
        for observation in self.observations:
            if observation.category_id not in category_ids:
                raise ValueError('Forensic observation has no category definition')
            category = next(item for item in self.categories if item.category_id == observation.category_id)
            if observation.indicator_id != f'forensic:{category.original_label}':
                raise ValueError('Forensic indicator and original category label disagree')
            key = (observation.category_id, observation.period.ordinal)
            if key in seen:
                raise ValueError('Duplicate forensic category and reporting-quarter key')
            seen.add(key)
        return self
