# Task 08E — versioned forensic toxicology analytical adapter

Implemented an additive, source-specific backend contract for the existing Phase 4 forensic resource. The legacy forensic endpoint and all frontend consumers remain unchanged. No data, frozen artifact, statistical result, database schema/policy, dependency, or Phase 9 integration was modified.

## 1. Inspected evidence and verified definitions

Inspected the Task 08B baseline and preservation evidence, the Task 08C mortality adapter report and implementation, the Task 08D frontend migration report and implementation, the forensic raw source, Phase 4 outputs and run manifest, the current forensic API, and forensic-related frontend consumers and tests.

The requested standalone Task 08A Data Quality & Analytical Architecture Audit was not present in the workspace. The available Task 08B contract/preservation evidence and the Task 08C–08D reports were used alongside direct inspection of the forensic source and artifact. This does not substitute for review of the missing audit if it contains additional forensic-specific findings.

| Evidence | Verified fact |
|---|---|
| Raw source | `datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv`; fields are `Quarter`, `drug_name`, `measure`, `value` |
| Source provenance | Public Health Scotland; RADAR dashboard URL is recorded in the Phase 4 manifest and source register; source SHA-256 `ccba2a3158b69e38194cafb415dba8834cf080c9174721299977037c4a8bb0df` |
| Source measurements | All 210 source rows use `measure=Number`; all values are nonnegative integer counts, from 0 to 489 |
| Reporting periods | 30 calendar quarters, Q4 2018 through Q1 2026 |
| Source categories | All Benzodiazepines; Dissociatives; Gabapentinoids; Opioids; Prescribable Benzodiazepines; Stimulants; Street Benzodiazepines |
| Phase 4 artifact | `analysis/phase4/outputs/forensic_counts.csv`, 210 rows, analytical version `phase4-1.0.0`, SHA-256 `6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063` |
| Artifact measure | `unit=detection_count`, `period_basis=calendar_quarter`; the artifact carries unchanged descriptive comparisons, rolling/reference fields and ranks |
| Known limitations | Categories overlap; counts are not unique deaths or people. No sample denominator or population prevalence is available. Source publication date is unknown; source data cutoff is 2026-03-31. |

Phase 4 documentation explicitly describes the seven categories as overlapping and cautions that testing/sample changes and absent denominators preclude prevalence estimates. The raw source provides category labels but no detailed chemical inclusion definitions. The contract therefore preserves each exact label, marks the category definition as `source_label_only`, and does not invent a more specific definition. The source does not supply a testing/sample definition or denominator; those contract fields are explicitly null.

## 2. Forensic-specific contract

Contract version: **`forensic-toxicology/1.0.0`**  
Route: **`GET /api/v1/analytical/v1/forensic-toxicology`**

The response contains source, verified artifact, measure, category definitions, research metadata, pagination and observations. Each observation carries its source indicator/category ID, exact original category label by reference, both original and canonical quarter labels, period dates/order, count value, availability, sample geography, source limitations and unchanged Phase 4 descriptive context.

The contract separates the source’s original measure label (`Number`) from the Phase 4 unit (`detection_count`). Because the verified source observations are integer counts, observations accept only nonnegative strict integers or null with a matching unavailable status. The adapter does not recompute the existing descriptive statistics; it carries them in `research_context`.

Representative response excerpt:

```json
{
  "contract_version": "forensic-toxicology/1.0.0",
  "source": {
    "source_id": "radar_toxicology_forensic_2018-2026.csv",
    "source_version": "ccba2a3158b69e38194cafb415dba8834cf080c9174721299977037c4a8bb0df",
    "publisher": "Public Health Scotland",
    "publication_date": null,
    "source_data_cutoff": "2026-03-31"
  },
  "artifact": {
    "resource": "forensic",
    "analytical_version": "phase4-1.0.0",
    "artifact_sha256": "6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063"
  },
  "measure": {
    "source_measure": "Number",
    "unit": "detection_count",
    "period_basis": "calendar_quarter",
    "sample_or_testing_definition": null,
    "sample_denominator": null
  },
  "observations": [{
    "indicator_id": "forensic:Opioids",
    "period": {
      "label": "2018 Q4",
      "original_label": "Q4 2018",
      "period_start": "2018-10-01",
      "period_end": "2018-12-31"
    },
    "value": 42,
    "availability_status": "observed"
  }]
}
```

The live response also includes complete artifact provenance, all seven category definitions, stable identities, original row ordering, pagination metadata and the preserved descriptive context.

## 3. Observation identity and category safeguards

Category IDs are deterministic hashes scoped to the contract version, source ID, source SHA-256 and exact original category label. Observation IDs include the contract version, source identity/version, analytical version and artifact hash, complete measure definition, source-specific category definition and indicator ID, sample geography, and both original and canonical reporting-quarter identity. The observed value is not an identity dimension; a changed source/artifact version yields new version-scoped identities.

The collection token hashes the complete ordered response content, including values and metadata. No categories are renamed or merged. Category metadata explicitly states `overlapping_source_groups` and `additive=false`; the API makes no category sums or estimates of unique deaths, people, or prevalence.

## 4. Files created or modified

Added:

- `backend/schemas/forensic_v1.py` — strict typed contract and source-specific validation.
- `backend/services/forensic_adapter.py` — verified source/artifact loading, source-to-artifact parity, identities, pagination and complete-collection verifier.
- `backend/api/forensic_v1.py` — separate read-only versioned route.
- `backend/tests/test_forensic_adapter.py` — immutable-baseline equivalence, validation, identity, pagination and legacy-route regression tests.
- This report.

Modified:

- `backend/main.py` — registered the additive forensic router.
- `backend/tests/test_mortality_adapter.py` — updated the OpenAPI-addition assertion to allow the new forensic path while continuing to compare every existing path unchanged. No mortality endpoint, schema, identity, or response behavior was changed.

The pre-existing Task 08E baseline files were read and not overwritten.

## 5. Baseline equivalence

The pre-implementation forensic baseline under `docs/baselines/task08e/forensic-baseline.json` records successful comparisons with Task 08B. The new tests independently compare the live adapter projection and current source/artifact to those immutable Task 08B records and fingerprints; they do not rely only on two transformations of the current data.

| Invariant | Verification |
|---|---|
| Observations | All 210 artifact/API observations retained |
| Original values | Exact ordered response and numeric-projection fingerprints match Task 08B |
| Missingness and zero | Baseline has 0 null values and 1 observed zero; both states are preserved (the model also enforces consistent null availability) |
| Categories and quarters | All seven exact source labels and all 30 source quarters retained |
| Measure and unit | Original `Number`, artifact `detection_count`, and calendar-quarter basis preserved |
| Existing Phase 4 fields | Legacy reconstruction matches the complete Task 08B response field set, including descriptive values and nulls |
| Provenance and artifact | Source SHA, artifact SHA, analytical version, paths and metadata match Task 08B |
| Raw source and artifact rows | All 210 raw source rows and all 210 artifact rows match their Task 08B file fingerprints |

Task 08B fingerprints: ordered forensic response `279211b429f4a2827f0722673fd45874ba0bff2fed41a31de1855ad2c5c79cc0`; numerical projection `52263d96c5020cfa500eb2225fbcdddeb8c5a7becae14ebffc00e33c7b498013`. The baseline’s ten forensic cross-checks all pass, and its 85 source/research manifest entries still match.

## 6. Pagination and failure handling

Pagination defaults to 100 records and permits limits 1–1,000. Nonzero offsets require the first page’s `expected_collection` token. Pages preserve the Phase 4 artifact’s original row order. Changed collections return **409**; invalid bounds, malformed parameters and out-of-range offsets return **422**. Source/artifact integrity or schema failures use the existing explicit **503 unavailable-evidence** response.

The independent `collect_forensic_pages` verifier rejects gaps, overlap, no-progress or surplus pages, duplicate observations, mixed metadata/tokens, invalid category/observation identities, incomplete totals and content that does not match the complete collection token. The loader verifies the Phase 4 artifact through the existing checksum-verifying repository, then validates the manifest/source hashes and matches each source measurement to its corresponding artifact category-quarter key.

## 7. Validation and regression results

- **Backend:** 66 passed, 0 failed.
- **Frontend unit tests:** 91 passed, 0 failed.
- **Browser tests:** 38 passed, 0 failed. Existing forensic frontend behavior remains on the legacy route; no consumer was migrated.
- **Production build:** passed; 31 modules.
- **Source/research manifests:** 85/85 matched.
- **Pylance:** no diagnostics in the new schema, adapter or route.
- **Whitespace:** `git diff --check` passed.

The backend run reported the existing Starlette/httpx TestClient deprecation warning; no dependency was added or changed. The new tests also prove the old forensic endpoint’s baseline fingerprint and preserve every pre-existing OpenAPI path, including the mortality analytical path.

## 8. Preservation verification

Compared with the pre-implementation Task 08E preservation snapshot, 348 of 350 previously captured files are unchanged. The only existing-file differences are the intended router registration in `backend/main.py` and the test assertion update described above. All 26 Task 08B, 10 Task 08C and 14 Task 08D baseline/evidence files remain byte-for-byte unchanged. No forensic source, frozen Phase 4 output, manifest, analytical/model code, frontend file, database schema/policy, dependency manifest or Phase 9 artifact changed.

The existing police mortality contract and Geographic Explorer migration remain unchanged at runtime. The backend regression suite, old mortality response fingerprint and existing OpenAPI path definitions passed. Browser tests passed without frontend changes.

## 9. Known limitations

- The standalone Task 08A audit was unavailable in the workspace.
- The raw source does not define the chemical composition of its category labels, testing-frame details, sample size or denominator; these remain explicitly unknown.
- Source publication date is unknown. The source cutoff and analysis date are retained without implying current observations.
- These are source-reported detection counts in a forensic testing sample, not causal deaths, unique people, mutually exclusive categories or population prevalence.
- Baseline equivalence proves preservation, not scientific validity or independent source collection.

## 10. Recommendation

Review the contract, especially the source-label-only category definitions and unavailable testing denominator, before authorizing any frontend migration. Task 08E stops at the forensic backend adapter; no frontend consumer, screen or Phase 9 integration was changed.
