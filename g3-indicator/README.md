# Scotland drug harm early-warning indicator (prototype)

Project folder for the MSc group indicator, individual 5 work and the implementation (Chapter 4).

## Layout
- `src/`, `index.html`, `public/`: Vite front end (vanilla JavaScript, Chart.js, Leaflet). Run `npm install`, then `npm run dev`.
- `scraper/`: Python scripts that collect published RADAR alert pages. Respects robots.txt, waits between requests, saves raw HTML with checksums.
- `data/raw/`: raw downloads and scraped HTML (not edited).
- `data/derived/`: tables built from raw data (for example `alerts_scraped.csv`).
- `data/frozen/`: frozen parameters, calibration and alert rule decisions, with checksums (copy from the analysis folder).

## Status
- Front end: placeholder page that loads `public/data/quarterly_input_table.json` once exported.
- Scraper: seeded with the RADAR alerts index only. Add seed URLs for each quarterly report's alerts section after checking the terms of use.
- Not yet built: database (Supabase), API, indicator outputs, alert overlay.

## Rules for the scraper
- Only fetch pages allowed by robots.txt.
- Record the URL, retrieval time and checksum for every saved file.
- Leave fields blank when they are not found. Do not infer publication codes.
