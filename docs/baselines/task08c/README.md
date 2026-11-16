# Task 08C evidence

See [the completion report](../../TASK08C_MORTALITY_ADAPTER_REPORT.md) for contract specification, identity algorithm, missingness, baseline equivalence, tests and limitations.

This new directory is separate from the immutable Task 08B capture. Its contents include:

- `example-response.json`: actual ASGI GET response for the new route with `limit=1`.
- `openapi-addition.json`: only the new route and typed contract schemas.
- `backend-tests.txt`, `frontend-tests.txt`, `browser-tests.txt`, `build.txt`: current regression results; logs are UTF-8.
- `task08b-preservation-before.json`: SHA-256 values of all 26 Task 08B evidence files, read without rewriting them.
- `verify_preservation.py`, `preservation-verification.json`: comparison with Task 08B's original 293-file snapshot, explicitly permitting only the existing-file router integration in `backend/main.py`, and rechecking all 85 manifest entries.

Results: **49 backend tests, 83 frontend tests and 35 browser tests passed; production build passed**. **292/293** original protected files are unchanged; the authorised two-line `main.py` integration is reported separately. Four new application/test modules are additions, not changes to frozen research. All 26 Task 08B evidence files and 85 manifest checks are preserved. No other resource was migrated.

The preservation verifier writes only this directory. It must not be replaced by rerunning Task 08B capture. Hash equivalence and regression tests establish preservation, not scientific or operational validity. No database schema, permission or data changes were performed.
