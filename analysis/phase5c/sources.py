"""Versioned compatibility registry and verified gap-resolution pathways."""
from collections import Counter
from analysis.phase5c.compatibility import geo

PHS = 'https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-january-2025/'


def registry(observations):
    output=[]
    for dataset in sorted({r['dataset'] for r in observations}):
        rows=[r for r in observations if r['dataset']==dataset]
        sample=rows[0]
        output.append(dict(dataset=dataset, source_id=sample['source_id'],source_path=sample['source_path'],source_sha256=sample['source_sha256'],
                           source_url=sample['source_url'],indicator_definitions=sorted({r['indicator_id'] for r in rows}),
                           units=sorted({r['unit'] for r in rows}),substances=sorted({r['substance_category'] for r in rows if r['substance_category']}),
                           geographies=sorted({r['geography'] for r in rows}),period_basis=sample['period_basis'],
                           geographic_scope_metadata=[dict(raw_name=name,**geo(name)) for name in sorted({r['geography'] for r in rows})],
                           first_period=min(rows,key=lambda r:int(r['ordinal']))['period'],last_period=max(rows,key=lambda r:int(r['ordinal']))['period'],
                           source_data_cutoff=sample['source_data_cutoff'], publication_date=sample['publication_date'] or None,
                           reporting_lag='Unknown for this saved vintage; observation age is not publication lag',
                           source_population=sample['geography'] if dataset not in ('mortality_quarterly','naloxone_weekly') else 'Separate national and regional operational aggregates',
                           denominator='Original arithmetic-checked numerator/denominator in frozen input; independent lineage unresolved' if dataset=='frozen_forensic_shares' else 'No compatible testing/sample/exposure denominators in imported CSV',
                           completeness=dict(observations=len(rows),missing=sum(r['observed_value']=='' for r in rows),states=dict(Counter(r['classification'] for r in rows))),
                           possible_dependence='Counts and frozen forensic shares share testing lineage; other sources may share people/cases; independence not established',
                           limitations=sample['limitations'], boundary_rule='National testing samples, police divisions, boards and unknown areas retained separately'))
    return output


def gaps():
    entries=[
        ('forensic_denominator','Forensic counts cannot establish positivity/prevalence','Original forensic laboratory quarterly tested-sample totals and panel metadata','Historical frozen shares only, not extended beyond 2024','unresolved','No denominator or annual-to-quarter conversion inferred'),
        ('treatment_denominator','Treatment detection counts depend on tests/cohort','PHS RADAR / NHS GG&C laboratory urine-test counts by month and category','Compare recorded counts with explicit testing-exposure caveat','unresolved','SDMD treatment assessment counts are a different outcome and cannot supply this denominator'),
        ('assist_periods_samples','ASSIST percentages lack exact interval and sample size','PHS ASSIST study period recruitment dates and tested n, by site/panel','Keep source study labels and explicit insufficient_data','unresolved','Rounded percentages do not uniquely determine n; no reverse-engineering'),
        ('category_panel_changes','Broad substance groups overlap and tests may change','Laboratory panel/version metadata and PHS technical notes','Explicit mapping dictionary, unmatched/overlap status and no sum of categories','partially_resolved','Engineering mappings do not establish temporal panel equivalence'),
        ('naloxone_recording','Weekly counts may cross a recording-system change',PHS,'Mark April 2024 rollout context; do not splice or adjust counts','partially_resolved','Official January 2025 continuity notes identify rollout; board dates/effect magnitude still unknown'),
        ('mortality_vintage','Legacy and Databelt definitions/revisions may differ','analysis/phase3/official_source_review.json; Police Scotland methodology','Keep frozen legacy vintage; no later incompatible append','unresolved','Registered NRS deaths are not a replacement suspected-death numerator'),
        ('publication_dates','Historical warning availability cannot be reconstructed','Original release archives and extract manifests by source','Keep unknown dates; retrospective comparisons only','unresolved','January 2025 report publication date does not date the saved 2026 CSV vintage'),
        ('geographic_population','No verified Greenock series or compatible rate join','NRS council tables/population boundary metadata; local aggregate release if available','Wider-area labels and dashboard no-local-data state','partially_resolved','Health-board populations and council treatment counts cannot normalise police-division deaths'),
        ('foi_alert_reference','No complete external alert reference','Pending PHS FOI response','Local staging validator, quarantine, no-alert negatives forbidden, metrics gate closed','unresolved','No real response received or staged'),
        ('blocked_public_download','New aggregate vintage not acquired','analysis/phase3/acquire_radar.mjs and official PHS dashboard','Continue saved supported data; source-level harmonisation required','unresolved','Earlier approval-review limit not bypassed or retried'),
    ]
    return [dict(gap=k,affected_analysis=a,potential_official_source=s,available_workaround=w,status=t,interpretation_consequence=c) for k,a,s,w,t,c in entries]


def official_review():
    return dict(reviewed_on='2026-11-10',source_url=PHS,published='2025-01-28',
                located_section='Data sources and limitations / Naloxone administration by Scottish Ambulance Service / Continuity of data',
                verified_finding='A new clinical recording IT system began rollout in April 2024; no board-specific effect size is established here.',
                consequence='Treat as potential measurement break, not evidence of changed toxicity. Seasonal behaviour is also described in that report.',
                limitations='This documents the report, not a checksum of its live HTML or the original 2026 CSV extraction. No dataset download attempted.',
                statistical_reference='https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html')
