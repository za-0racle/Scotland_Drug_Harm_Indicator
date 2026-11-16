# Task 08B — frozen preservation matrix

Exact file-level SHA-256 values are in `preservation-before.json`; after-check results are in `preservation-verification.json`. No comparison is a scientific revalidation.

| Protected group | Files |
|---|---:|
| research_and_processing | 146 |
| application_and_tests | 81 |
| original_sources | 43 |
| legacy_frozen | 15 |
| root_imports | 8 |

The snapshot includes all original-source files, nonscratch research outputs and processing code, legacy frozen assets, root imports, application code, models/configuration source, dependencies lockfile and regression tests. Excludes credentials/environment files, dependencies, bytecode, test scratch, generated builds/screenshots and this new documentation directory. `manifest-verification.json` separately records 18 original-source and 67 research-output manifest comparisons, including isolated Phase 9 artifacts. Isolation is preserved; inventory is not integration.

`file-inventory.json` records actual CSV rows/fields/empty values and parsed JSON shapes. `resource-contracts.json` adds full-response and numerical-projection fingerprints. File hashes detect any byte change; ordered fingerprints intentionally also change if record order changes. Metadata-only changes may alter full-response fingerprints while numerical fingerprints remain stable. Source-vintage IDs/checksums are part of the evidence and must not be replaced silently.
