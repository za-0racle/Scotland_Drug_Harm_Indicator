# Scotland Drug Harm Indicator

Run the application from the repository root with `npm install` and `npm run dev`. Build with `npm run build`.

Copy `.env.example` to `.env.local` and set the Supabase project URL and publishable key. Restart Vite after changes. Never use secret or service-role keys in browser code.

`src/supabase.js` provides a reusable publishable-key client. `src/database.js` reads only the approved mortality, configuration and result tables with explicit columns, chronological ordering and pagination. The analytical dashboard includes live summary cards, a mortality year-range filter, model selection, EWMA and separate two-sided CUSUM components, exact-value tables, recorded retrospective flags, parameters and provenance. Missing observations remain gaps. No visible rows can mean an empty table or row level security filtering data.

Run `npm test` for transformation and database reader tests, `npm run build` for production validation, and `npm run test:e2e` for live browser verification. Browser tests require the configured public read access and the current research dataset; they never mutate Supabase. They use installed Edge on Windows; on other systems install Chromium with `npx playwright install chromium`. Live browser screenshots are saved locally in `artifacts/section-4.6/` (ignored by Git).

See `docs/dashboard-phase-1.md` for implementation details, limitations and Section 4.6 screenshot locations. `docs/supabase-integration-review.md` is the earlier public-data review. Existing policies are preserved; do not apply the historical migration again or run `db push` automatically.

The repository root is the active frontend. `g3-indicator` contains research inputs used by analysis scripts; its former placeholder frontend is archived in `g3-indicator/prototype-archive/` and is no longer an npm app. Keep `g3-indicator/public/data/quarterly_input_table.json` in place unless its analysis references are updated.
