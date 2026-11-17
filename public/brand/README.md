# SDHI identity assets

The SDHI wordmark and compact symbol use charcoal, gold and ivory. The four-point line is an abstract analytical motif, not a plot of observations or a warning indicator. It contains no medical symbol, geographic boundary or agency mark.

- `sdhi-logo.svg`: application wordmark for light surfaces; `sdhi-logo-dark.svg` supplies light lettering for the dark theme.
- `sdhi-logo.png`: transparent 840 × 240 raster wordmark.
- `sdhi-icon.svg`, `sdhi-icon-192.png`, `sdhi-icon-512.png`: compact identity.
- `legacy-favicon.svg`: recoverable copy of the previous favicon, also retained in Git history.
- Root public assets: `favicon.svg`, multi-resolution `favicon.ico`, 180 × 180 `apple-touch-icon.png`, and exactly 1200 × 630 `og-image.png`.

Generate derivatives with `python scripts/build-brand-assets.py` from the repository root. The offline authoring script uses Pillow and Segoe UI (or DejaVu Sans); it is not part of the application build or a runtime dependency. SVG geometry and raster geometry are defined in that script. Font differences can affect raster wordmark widths across operating systems, so inspect regenerated images before use.

The social preview identifies the research dashboard and domain without numerical claims. Initial HTML links use the owner's canonical host, `https://sdhi.cc/`. External preview rendering and caches require separate verification.
