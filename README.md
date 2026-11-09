# Scotland Drug Harm Indicator

Run the application from the repository root with `npm install` and `npm run dev`. Build with `npm run build`.

Copy `.env.example` to `.env.local` and set the Supabase project URL and publishable key. Restart Vite after changes. Never use secret or service-role keys in browser code.

`src/supabase.js` provides the client. `src/database.js` reads only the reviewed mortality, configuration and result tables with explicit columns, chronological ordering and pagination. The page shows separate loading, empty, error and data preview states. No visible rows can mean an empty table or row level security filtering data.

Run `npm test` for integration reader tests. See `docs/supabase-integration-review.md` for the data review and manual approval procedure. The proposed SQL migration is local only and has not been applied. Do not push it automatically.

`g3-indicator` is reference material, not the implementation directory.
