# Task 08D evidence

See [the completion report](../../TASK08D_FRONTEND_MIGRATION_REPORT.md) for scope, contract checks, baseline equivalence, rollback and limitations.

- `SELECTION.md` records the chosen Geographic Explorer police-source feed before implementation.
- `legacy-response.json` was verified against Task 08B's original full-response fingerprint and artifact metadata before capture; `contract-response.json` is the unchanged Task 08C backend response. Both are read-only captures, not recalculated research outputs.
- `fixture-verification.json` records baseline verification and fixture file hashes. Frontend tests compare mapped records/exports against this legacy fixture and independently verify the frozen CSV hash.
- `previous-task-integrity.json` pins 42 Task 08B/08C evidence and backend files at task start. `verify_preservation.py` reads those files and Task 08B's manifests without rewriting them; its output is `preservation-verification.json` in this new directory.
- `frontend-tests.txt`, `backend-tests.txt`, `browser-tests.txt`, `build.txt` contain final full-suite results. `browser-focused.txt` retains the initial resize-timing assertion failure; `browser-focused-final.txt` records the passing focused rerun after waiting for settled layout.

Final results: **91 frontend tests, 49 backend tests, 38 browser tests passed; production build passed**. **85/85** manifest checks and **42/42** prior-task files remain unchanged. Task 08D changes only two existing frontend integration files and adds a collector, mapper and focused tests. No backend contract, original dataset, frozen research result, model or permission changed.

The browser pins opaque collection tokens and independently verifies observation/geographic identities. It does not reproduce Python's complete floating-number JSON token encoding. Numeric and export equivalence use baseline-verified records; this evidence does not establish scientific external validation.
