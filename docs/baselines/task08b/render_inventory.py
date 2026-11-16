"""Render existing captured evidence, without changing application contracts."""
import json
import ast
from collections import Counter
from capture_baseline import ROOT, OUT, save, digest
from backend.services.platform import PlatformService
from backend.schemas import Filters


if __name__ == '__main__':
    resources = json.loads((OUT/'resource-contracts.json').read_text(encoding='utf-8'))
    tree = ast.parse((ROOT/'backend/main.py').read_text(encoding='utf-8-sig'))
    routes = next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='routes' for t in n.targets))
    paths = {}
    for path,key in routes.items(): paths.setdefault(key,[]).append('/api/v1/'+path)
    paths['anomalies']=['/api/v1/anomalies?signals_only=false']
    paths['enhanced']=['/api/v1/anomalies?model=<verified-method>&signals_only=false']
    # These are supported export aliases, not newly introduced routes.
    export_keys = {'annual','comparisons','rates','rate_comparisons','anomalies','enhanced','diagnostics','zero_baseline','backtest','forecast_observations','sensitivity','runs','model_metrics','evidence','forecast','forecast_models','mortality_trends','forensic','assist','treatment','naloxone','gaps'}
    for key in export_keys: paths.setdefault(key,[]).append('/api/v1/exports?resource='+key+'&format=json')
    lines=['# Task 08B — API contract inventory','',
           'Captured from the existing application, not a proposed replacement contract. `resource-contracts.json` contains every returned field, null count, complete-result fingerprint, artifact version and SHA-256. `openapi.json` records every route and query schema. No endpoint response was changed.','',
           '## Retrieval and response rules','',
           '- Verification uses production `PlatformService.query` in-process for all 28 catalog resources. Metadata routes and OpenAPI were additionally checked through ASGI GETs. This does not establish availability of a separately deployed API.',
           '- All-resource capture sets `signals_only=false`; `/anomalies` defaults to signals only. Enhanced HTTP selection requires a verified method, so its 31,512-row baseline is the union of methods or the enhanced export.',
           '- Common filters: `geography_id`, `boundary_type`, `indicator`, `category`, `model`, `compare_to`, `start_year`, `end_year`, `start_date`, `end_date`, `offset`, `limit`, `signals_only`. Exact constraints/defaults are in OpenAPI. Some fields apply only to particular resources; do not assume every filter is meaningful for every row shape.',
           '- Pagination: offset 0 by default, limit 100 by default, maximum 1,000; offset maximum 1,000,000. Exports are paginated too. Capture requested 1,000 and verified returned count against stable totals.',
           '- Envelope: `state, kind, data, total, offset, limit, metadata, message`. Empty matches are not zero harm or no official alerts. Null values remain distinct from zeros.',
           '- Artifact metadata: resource, storage, analytical version, execution timestamp, artifact SHA-256, source path, provenance manifest and limitations. Individual source publication/cutoff/definition fields vary by resource.',
           '- Exact-date filters exclude records lacking exact dates; they do not invent ASSIST dates. Geography identifiers identify scopes, not verified polygons.', '',
           '## Approved artifact resources','', '| Resource | Existing endpoint/access | Complete records / pages | Version | Unit / period / geography |','|---|---|---:|---|---|']
    for item in resources:
        d=item['definitions']; desc='; '.join(k+'='+', '.join(v) for k,v in d.items() if k in ('unit','period_basis','boundary_type')) or 'Not explicit at top level; inspect nested/source-specific definition'
        access='<br>'.join('`'+p+'`' for p in paths.get(item['resource'],[])) or 'Internal catalog/service only; no direct public route or admitted export'
        lines.append(f"| `{item['resource']}` | {access} | {item['api_records']:,} / {item['pages']} | {item['metadata']['analytical_version']} | {desc} |")
    lines += ['', '## Exact response fields and provenance', '']
    for item in resources:
        lines += ['### '+item['resource'], '', '- Artifact: `'+item['metadata']['source_path']+'`', '- SHA-256: `'+item['metadata']['artifact_sha256']+'`', '- Returned fields: `'+', '.join(item['fields'])+'`', '- Definition/model values: `'+json.dumps(item['definitions'],ensure_ascii=False)+'`', '- Source scope and availability: `'+json.dumps(item.get('source_scope_and_availability',{}),ensure_ascii=False)+'`', '']
    lines += ['## Database, metadata and dynamic routes','',
              '| Endpoint | Existing contract / scope |','|---|---|',
              '| `/mortality/quarterly` | Reviewed DB projection; national police counts; 36 live rows verified separately. |',
              '| `/monitoring/configurations` | Reviewed DB projection; 4 configurations; parameters preserved via ordered value fingerprint. |',
              '| `/monitoring/results` | Reviewed DB projection; 76 results; signed statistics and nullable limits/CUSUM fields. |',
              '| `/health` | API health only; explicitly does not prove DB health. |',
              '| `/overview` | Composite live DB/artifact state; independent resource failures, not one homogeneous observation list. |',
              '| `/geographies` | 33 scopes, including unavailable Greenock; registry, not boundary geometry. |',
              '| `/geographies/{id}` | One registry profile or rejected unknown identity. |',
              '| `/geographies/{id}/{section}` | sections: indicators, trends, anomalies, evidence, comparisons; source/boundary-aware service selection. Comparisons require admitted compatible peers. |',
              '| `/indicators` | Definitions assembled from six source families; units and period bases retained. |',
              '| `/sources`, `/sources/gaps` | Compatibility metadata and evidence gaps; not observed outcomes. |',
              '| `/methodology`, `/validation/status`, `/reports` | Research limitations, validation status and report metadata. |','',
              'All paths above have `/api/v1` prefix. Full parameter names, types, response schemas, route enums and export allowlist are in `openapi.json`. Dynamic area outputs are selection-dependent; their counts are not one fixed dataset. See `database-verification.json` for projected fields and live checks. No Phase 9 route is admitted.']
    (OUT/'API_CONTRACTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    hashes=json.loads((OUT/'preservation-before.json').read_text(encoding='utf-8'))
    groups=Counter('original_sources' if p.startswith('datasets/') else 'research_and_processing' if p.startswith('analysis/') else 'legacy_frozen' if p.startswith('g3-indicator/') else 'root_imports' if p.startswith('group3') else 'application_and_tests' for p in hashes)
    (OUT/'PRESERVATION_MATRIX.md').write_text('# Task 08B — frozen preservation matrix\n\nExact file-level SHA-256 values are in `preservation-before.json`; after-check results are in `preservation-verification.json`. No comparison is a scientific revalidation.\n\n| Protected group | Files |\n|---|---:|\n'+'\n'.join(f'| {k} | {v} |' for k,v in groups.items())+'\n\nThe snapshot includes all original-source files, nonscratch research outputs and processing code, legacy frozen assets, root imports, application code, models/configuration source, dependencies lockfile and regression tests. Excludes credentials/environment files, dependencies, bytecode, test scratch, generated builds/screenshots and this new documentation directory. `manifest-verification.json` separately records 18 original-source and 67 research-output manifest comparisons, including isolated Phase 9 artifacts. Isolation is preserved; inventory is not integration.\n\n`file-inventory.json` records actual CSV rows/fields/empty values and parsed JSON shapes. `resource-contracts.json` adds full-response and numerical-projection fingerprints. File hashes detect any byte change; ordered fingerprints intentionally also change if record order changes. Metadata-only changes may alter full-response fingerprints while numerical fingerprints remain stable. Source-vintage IDs/checksums are part of the evidence and must not be replaced silently.\n',encoding='utf-8')
    service=PlatformService(); identities=[]
    keymap={'mortality_trends':['source_sha256','indicator_id','geography','period_basis','period'],
            'forensic':['source_sha256','indicator_id','geography','period_basis','period'],
            'assist':['source_sha256','indicator_id','geography','period_basis','period'],
            'treatment':['source_sha256','indicator_id','geography','period_basis','period'],
            'naloxone':['source_sha256','indicator_id','geography','period_basis','period'],
            'annual':['source_sha256','indicator_id','geography','year'],
            'enhanced':['observation_id','method','window'], 'diagnostics':['observation_id','method','window'],
            'rates':['geography','period_start','period_end','source_sha256'],
            'backtest':['model','origin','target','horizon'],
            'forecast':['model','forecast_origin','target_period','horizon_quarters']}
    for resource,fields in keymap.items():
        rows=[];offset=0
        while True:
            env=service.query(resource,Filters(offset=offset,limit=1000,signals_only=False));rows.extend(env.data)
            if len(rows)>=env.total:break
            offset+=len(env.data)
        values=[{k:r.get(k) for k in fields} for r in rows]
        identities.append(dict(resource=resource,fields=fields,records=len(rows),missing_key_records=sum(any(r.get(k) is None for k in fields) for r in rows),
                               duplicate_keys=len(values)-len({digest(v) for v in values}),ordered_identity_fingerprint=digest(values)))
    save('identity-verification.json',identities)
    print('Rendered inventory and preservation matrix; captured explicit identity checks.')
