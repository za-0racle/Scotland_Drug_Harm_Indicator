# G3 research inputs

This directory is not a runnable application. The active dashboard is at the repository root; use the root `package.json` for frontend commands.

## Contents
- `prototype-archive/`: source-only copy of the retired placeholder frontend. It has no npm manifest and is not part of the active dashboard.
- `public/data/quarterly_input_table.json`: frozen research input used by analysis scripts. Keep this path stable unless all analysis references and manifests are updated.
- `data/derived/`: derived research tables, including the curated alert list.
- `data/frozen/`: frozen parameters, calibration and alert-rule decisions.
- `scraper/`: research scraper for published RADAR alert pages.

The scraper must only fetch pages allowed by robots.txt, record the URL, retrieval time and checksum for each saved file, and leave fields blank when they are not found.
