# SDHI Phase 1 — Shared design, branding and metadata

Date: 17 November 2026. Phase 1 implemented locally against the approved Task 08S baseline. Phase 2 screen rearrangement has not started. Publication and external sharing-preview acceptance remain outstanding.

## Implemented

The existing Vite, vanilla JavaScript and Chart.js application retains all eight primary screens and every hash-route alias. Shared typography, card padding, control sizing, table text, chart legends and spacing now use the existing white, gold and charcoal identity with more readable supporting text. The shared presentation layer is imported after the existing styles; source-specific components remain in place.

Navigation uses the eight approved labels. The global **Compare data** action opens the dedicated comparison workflow. The original dialog remains available as **Quick area comparison** on its previously supported screens, preserving its selections and export. The mobile drawer follows the measured toolbar height, including wrapped titles, rather than relying on a fixed offset. Focus trapping, Escape, active routes and theme switching are retained.

Shared copy uses **Refresh data** and **Sources and analysis details**. Transport errors use reader-facing explanations while preserving their distinct error codes and empty/unavailable states. Historical cutoffs, non-operational signal meaning, lack of PHS endorsement and geographic limitations remain accessible. Screen-specific findings and analytical order are deferred to Phase 2.

## Branding and metadata

Created an SDHI wordmark, light/dark variants and compact square analytical symbol. The motif is abstract branding with no numerical, medical, geographic or official-agency claim. The former favicon is retained in Git history and as `public/brand/legacy-favicon.svg`.

Production assets include SVG/PNG wordmarks, a square SVG, 192 × 192 and 512 × 512 PNG icons, a real six-size ICO (16–256 pixels), a 180 × 180 Apple touch icon and an exactly 1200 × 630 PNG social image. The offline authoring script uses the available Pillow installation; no application dependency was added. [Asset details](../public/brand/README.md).

Initial HTML now includes the requested title and description, canonical `https://sdhi.cc/`, Open Graph website/name/title/description/URL/image/dimensions/type/alternative text, Twitter large-image metadata, English language, viewport, theme colour and icon links. No social account was invented. All canonical and social URLs use the requested apex host.

## Files changed

| Area | Files |
| --- | --- |
| Entry and shared presentation | `index.html`, `src/main.js`, `src/platform/shared.css`, `src/platform/shell.js`, `src/platform/dashboard.js`, `src/platform/charts.js` |
| Shared labels and service messages | `src/platform/presentation.js`, `src/platform/overview.js` (source-details label only), `src/api/client.js`, `vite.config.js` |
| Asset source and outputs | `scripts/build-brand-assets.py`, `public/brand/` (wordmarks, symbols, PNG variants, legacy favicon and README), `public/favicon.svg`, `public/favicon.ico`, `public/apple-touch-icon.png`, `public/og-image.png` |
| Automated verification | `tests/branding.test.js`, `tests/shell.test.js`, `tests/platform.test.js`; `e2e/branding.spec.js`, `e2e/shell.spec.js`, `e2e/comparison.spec.js`, `e2e/comparison-studio.spec.js`, `e2e/geography.spec.js`, `e2e/acceptance.spec.js` |
| Documentation and screenshots | This report, the four previously prepared Task 08S baseline documents, and `docs/images/task08s-phase1/` |

The baseline audit's actual filename is `TASK08S_PHASE1_CONTENT_AUDIT.md`. Its planning statements are retained as the historical review record; this report records the subsequent implementation authorisation and outcome.

## Verification

| Check | Result |
| --- | --- |
| Frontend unit suite | 110 passed, including initial metadata and binary-format/dimension checks |
| Final Vite production build | Passed; 36 modules transformed |
| Built HTML and asset HTTP requests | Initial HTML and 11 asset URLs passed on local Vite preview; no HTML fallback for image/icon assets |
| PNG/ICO validation | PNGs decoded with required dimensions; ICO decoded with all six resolutions; metadata keys unique and built local references resolved |
| Shared-shell and acceptance browser suite | 15 passed; all eight screens, data rendering, chart legend interaction, comparisons/exports, bootstrap history, snapshot pagination, failure/empty/unavailable states, keyboard and themes |
| Additional geographic/comparison suite | 6 passed; geographic boundaries, 14-board peer group, profiles, published rates, category comparisons, source switching and independent failures |
| Responsive checks | 320, 390, 768, 1024 and 1440 pixels; no horizontal page overflow in shell checks; mobile drawer follows actual toolbar geometry |
| Console and contrast samples | No browser errors in the all-screen and shared-branding checks; sampled text contrast exceeded 4.5:1. These are targeted checks, not accessibility certification |
| Research and dependency preservation | Git comparison against HEAD showed no changes under backend, analysis, datasets, research inputs or Supabase, or to dependency manifests and `.gitattributes` |

The first sandboxed unit-test attempt could not spawn Node workers (`EPERM`). The same suite then passed with the required process permission. Local browser checks used the configured real application datasets; deliberate intercepted failures and malformed responses were confined to labelled regression tests. No fabricated data path was added to the application.

Actual local screenshots: [desktop shell](images/task08s-phase1/shell-desktop.png), [mobile shell](images/task08s-phase1/shell-mobile.png), [mobile navigation](images/task08s-phase1/shell-mobile-navigation.png). The existing analytical component order is intentionally still visible in these captures.

## Public verification and remaining work

Read-only HTTPS requests to `https://sdhi.cc/` on 17 November returned HTTP 200 after redirecting to `https://www.sdhi.cc/`. The public HTML still had the previous title and no Open Graph/Twitter/canonical tags. The new OG, ICO, Apple and 192/512 icon URLs returned HTTP 404; the previous SVG favicon returned HTTP 200. This verifies the existing deployment, not publication of this commit. Local HTTP evidence is saved under `artifacts/task08s-phase1/` (ignored by Git).

The changes are prepared for the existing deployment workflow and have not been pushed or deployed. After publication, repeat the public initial-HTML and asset checks. The hosting redirect currently favours `www`, while the supplied canonical specification uses the apex host; reconcile that hosting preference separately without silently changing the requested metadata. WhatsApp, Facebook, LinkedIn and other external preview rendering/caches were not tested.

No research-method, API, database, statistical-result or frozen-output change was made. Production analytical recovery is not established by this shared-design task. Stop here and report Phase 1 before beginning the separately supplied Phase 2 instructions.
