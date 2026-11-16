"""Typed contract for Phase 4 police mortality only; not model-statistic schemas."""
from typing import Annotated, Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(min_length=1, pattern=r'\S')]
SHA256 = Annotated[str, StringConstraints(pattern=r'^[0-9a-f]{64}$')]
Count = Annotated[int, Field(ge=0)]
CONTRACT_VERSION = 'mortality-trends/1.0.0'


class StrictRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', allow_inf_nan=False)


class SourceDefinition(StrictRecord):
    source_id: Text
    source_version: SHA256
    source_path: Text
    source_url: Text
    publication_date: Text | None
    publication_status: Text
    source_data_cutoff: Text | None


class IndicatorDefinition(StrictRecord):
    indicator_id: Literal['suspected_deaths']
    definition: Literal['Police Scotland provisional originally suspected drug deaths; not NRS registered deaths or population-adjusted risk.']
    unit: Literal['count']
    period_basis: Literal['calendar_quarter_legacy_10_day_adjustment']
    original_reporting_qualification: Text
    scientific_status: Text
    calculation_method: Text
    year_comparison_basis: Text
    rolling_periods: Annotated[int, Field(gt=0)]
    reference_periods: Annotated[int, Field(gt=0)]


class ArtifactDefinition(StrictRecord):
    resource: Literal['mortality_trends']
    analytical_version: Text
    artifact_sha256: SHA256
    source_path: Literal['analysis/phase4/outputs/mortality_quarterly.csv']
    provenance_manifest: Literal['analysis/phase4/outputs/run_manifest.json']
    storage: Literal['approved_local_artifact']
    executed_at_utc: Text
    limitations: list[Text]


class ResearchMetadata(StrictRecord):
    analysis_as_of: Text
    data_age_days: Count


class GeographyScope(StrictRecord):
    geography_id: Text
    canonical_name: Text
    original_name: Text
    boundary_type: Literal['country', 'police_division']


class Quarter(StrictRecord):
    year: Annotated[int, Field(ge=1900, le=2100)]
    quarter: Annotated[int, Field(ge=1, le=4)]
    label: Text
    ordinal: int
    period_start: Text
    period_end: Text

    @model_validator(mode='after')
    def exact_quarter(self):
        if self.label != f'{self.year} Q{self.quarter}' or self.ordinal != self.year * 4 + self.quarter - 1:
            raise ValueError('Inconsistent quarterly label or ordering')
        start = date(self.year, self.quarter * 3 - 2, 1)
        end = date(self.year + 1, 1, 1) if self.quarter == 4 else date(self.year, self.quarter * 3 + 1, 1)
        if (self.period_start != start.isoformat()
                or date.fromisoformat(self.period_end).isoformat() != self.period_end
                or date.fromisoformat(self.period_end).toordinal() != end.toordinal() - 1):
            raise ValueError('Inconsistent provided quarterly dates')
        return self


class ResearchContext(StrictRecord):
    """Existing frozen descriptive fields, carried unchanged; never recomputed."""
    share_of_national_pct: float | int | None
    previous_value: Count | None
    period_change: int | None
    period_change_pct: float | int | None
    year_reference_value: Count | None
    year_change_pct: float | int | None
    rolling_average: float | int | None
    historical_reference_mean: float | int | None
    reference_change_pct: float | int | None
    direction: Text
    percentage_point_change: float | int | None
    comparison_status: Text
    publication_lag_days: Count


class MortalityObservation(StrictRecord):
    observation_id: Annotated[str, StringConstraints(pattern=r'^mortality-observation:v1:[0-9a-f]{64}$')]
    geography: GeographyScope
    period: Quarter
    value: Count | None
    availability_status: Literal['observed', 'missing_or_suppressed']
    research_context: ResearchContext

    @model_validator(mode='after')
    def value_availability(self):
        if (self.value is None) != (self.availability_status == 'missing_or_suppressed'):
            raise ValueError('Availability and observation value disagree')
        return self


class Pagination(StrictRecord):
    total: Count
    offset: Count
    limit: Annotated[int, Field(ge=1, le=1000)]
    returned: Count
    next_offset: Count | None
    page_is_complete_collection: bool
    collection_token: SHA256
    ordering: Literal['original_artifact_row_order'] = 'original_artifact_row_order'


class MortalityPage(StrictRecord):
    contract_version: Literal['mortality-trends/1.0.0'] = CONTRACT_VERSION
    source: SourceDefinition
    indicator: IndicatorDefinition
    artifact: ArtifactDefinition
    research_metadata: ResearchMetadata
    pagination: Pagination
    observations: list[MortalityObservation]
