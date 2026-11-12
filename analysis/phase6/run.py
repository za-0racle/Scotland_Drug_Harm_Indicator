"""Local geographic case study; no database, frontend or earlier-output writes."""
import argparse
import csv
import json
import platform
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

from analysis.phase5c.run import preserve as previous_preserve
from analysis.phase6.data import ROOT,WORKBOOK,sha,extract,inspect_population,INDICATOR
from analysis.phase6.analytics import trends,comparisons,rate_comparisons,extrema,change

HERE=ROOT/'analysis/phase6'
POPULATION_PATHS=[ROOT/'datasets/Group3_Item2_Data/nhs_scotland_population_estimates_hb2019.csv',
                  ROOT/'datasets/Additional_Group3_Item2_Data/Scotland_population_estimate/hb2006_pop_est_01072020.csv']


def preserve():
    result=previous_preserve()
    for path in (ROOT/'analysis/phase5c').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            result[path.relative_to(ROOT).as_posix()]=sha(path)
    manifest=json.loads((ROOT/'analysis/phase5c/outputs/run_manifest.json').read_text())
    for name,expected in manifest['output_hashes'].items():
        if sha(ROOT/'analysis/phase5c/outputs'/name)!=expected:
            raise ValueError('Previous Phase 5C output changed: '+name)
    for name,expected in {**manifest['code_hashes'],**manifest['supporting_code_hashes']}.items():
        if sha(ROOT/name)!=expected:
            raise ValueError('Previous Phase 5C code changed: '+name)
    return result


def write_json(directory,name,value):
    (directory/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def write_csv(directory,name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (directory/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def hierarchy():
    return dict(interpretation='Evidence scopes, not interchangeable GIS polygons or a population allocation crosswalk',
                levels=[
                    dict(scope='Greenock',boundary_type='locality',role='focus_locality_no_direct_series',direct_observations=0,
                         finding='No Greenock-specific mortality/toxicity outcome is inferred',source=None),
                    dict(scope='Inverclyde',boundary_type='council',role='direct_case_study',direct_observations=15,
                         finding='Annual registered drug misuse deaths and published five-year ASRs',source='Table_C1 / Table_C4'),
                    dict(scope='K: Renfrewshire and Inverclyde',boundary_type='police_division',role='wider_context_only',
                         finding='Legacy quarterly suspected deaths, separate indicator and boundary',source='analysis/phase4/outputs/mortality_quarterly.csv'),
                    dict(scope='NHS Greater Glasgow and Clyde',boundary_type='health_board',role='wider_context_only',
                         finding='Weekly ambulance naloxone and monthly treatment urine detections, not council outcomes',source='analysis/phase4/outputs/naloxone_weekly.csv; treatment_counts.csv'),
                    dict(scope='Scotland',boundary_type='country',role='matched_registered_national_comparator',direct_observations=15,
                         finding='Same C1 registered definition and C4 published ASR; national total includes Inverclyde',source='Table_C1 / Table_C4')],
                rules=['Always display scope/boundary/indicator/period and vintage',
                       'Never downscale wider-area counts or rates to Greenock',
                       'Never merge registered and suspected deaths or use a health-board population for a council',
                       'No implied substance-specific toxicity mechanism from all-drug registered counts'])


def run(directory=None):
    before=preserve()
    inputs={p.relative_to(ROOT).as_posix():sha(p) for p in [WORKBOOK,*POPULATION_PATHS,ROOT/'group3_data_sources_import.csv',ROOT/'datasets/Group3_Item2_Data/MANIFEST.txt']}
    directory=Path(directory or HERE/'outputs').resolve()
    if directory!=HERE/'outputs' and not any(p.endswith('.local') for p in directory.parts):
        raise ValueError('Use phase6/outputs or a .local scratch path')
    directory.mkdir(parents=True,exist_ok=True)
    observations,rates,source=extract()
    annual=trends(observations);compared=comparisons(annual);rate_compared=rate_comparisons(rates)
    populations=inspect_population(POPULATION_PATHS)
    council=[r for r in annual if r['geography']=='Inverclyde']
    national=[r for r in annual if r['geography']=='Scotland']
    annual_rates=[dict(geography='Inverclyde',boundary_type='council',year=r['year'],indicator_id=INDICATOR,
                       deaths=r['observed_value'],population=None,rate_per_100000=None,status='unavailable_compatible_council_denominator',
                       reason='No verified same-year council population and allocation compatibility; health-board denominator rejected') for r in council]
    peaks=extrema(annual)
    latest=council[-1];national_latest=national[-1]
    early=[r['observed_value'] for r in council if 2010<=r['year']<=2014]
    late=[r['observed_value'] for r in council if 2020<=r['year']<=2024]
    delta,pct=change(sum(late)/5,sum(early)/5)
    findings=dict(indicator_id=INDICATOR,geography='Inverclyde',boundary_type='council',source_data_cutoff='2024-12-31',
                  publication_date='2025-09-02',analysis_as_of='2026-11-10',historical_not_current=True,
                  validated_annual_counts=[dict(year=r['year'],deaths=r['observed_value'],source_cell=r['source_cell']) for r in council],
                  latest=latest,matched_scotland_latest=national_latest,extrema=peaks,
                  nonoverlapping_five_year_blocks=dict(early_period='2010–2014',early_total=sum(early),early_annual_mean=sum(early)/5,
                                                       late_period='2020–2024',late_total=sum(late),late_annual_mean=sum(late)/5,
                                                       change_in_annual_mean=delta,change_pct=pct),
                  different_direction_years=[r['year'] for r in compared if r['direction_agreement']=='different'],
                  latest_published_rate_comparison=rate_compared[-1],
                  local_anomaly_feasibility=dict(status='not_estimated_insufficient_validation_support',observations=15,
                                                reason='Sparse annual 10–33 counts with trend and one revised vintage. A ten-year reference leaves only five targets; no externally validated local event labels or chosen annual null model.',
                                                interpretation='Peaks, changes and published rate intervals are descriptive; none is a statistically detected anomaly or warning'),
                  limitations=['Council outcomes cannot be assigned to Greenock','Counts are registrations, not exact event dates or all drug-attributable harm',
                               'NRS exclusions, classification and toxicology ascertainment can affect historical comparisons',
                               'No annual local crude rate or population-adjusted risk inferred from counts',
                               'Published five-year ASRs/intervals are imported, not independently recomputed; overlapping periods and nested geographies are dependent',
                               'Frozen 2024 vintage is not the latest NRS edition; no later counts appended',
                               'No model-generated local warning, causal substance inference or FOI-alert validation'])
    quality=dict(annual_observations=len(observations),inverclyde_years=len(council),scotland_years=len(national),
                 annual_quality_states=dict(Counter(r['quality_status'] for r in observations)),
                 published_five_year_rates=len(rates),five_year_total_matches=sum(r['total_check']=='matches_five_C1_counts' for r in rates),
                 suppression_policy='NRS [x]/[l]/[c]/[z], x, colon, empty and null remain missing; unknown symbols fail; zero remains an observed zero',
                 population_audit=populations,annual_rate_status='unavailable',published_five_year_ASR_status='verified_source_values_with_published_intervals',
                 uncertainty='No annual count confidence intervals manufactured; small-number caveats and original NRS C4 confidence bounds retained',
                 cross_checks=source['cross_checks'],geographic_allocation_limitation=source['geographic_allocation'])
    contract=dict(schema_version='phase6-1.0.0',status='local_dashboard_ready_not_deployed',
                  title='Inverclyde registered mortality: wider context for a Greenock-focused study',
                  default_geography='Inverclyde',greenock=dict(state='no_compatible_local_series',message='These are Inverclyde council outcomes; no Greenock-specific outcome is available'),
                  source=source,hierarchy=hierarchy(),annual_count_series=annual,matched_annual_comparisons=compared,
                  published_five_year_rates=rates,published_rate_comparisons=rate_compared,annual_crude_rates=annual_rates,
                  required_labels=['geography','boundary_type','indicator_id','period_basis','source_data_cutoff','publication_date'],
                  display_rules=['Draw gaps for missing values; never zero-fill','Label trailing means by their ending year; NRS published five-year rates by full period',
                                 'Do not label multi-year ASRs as annual crude rates','Show published confidence intervals and count/sampling/vintage caveats',
                                 'Keep suspected-death/police and health-board contexts in separate indicator sections',
                                 'No current threat colour, Greenock hotspot, clinical alert or significance inferred'],
                  findings=findings,public_or_database_write='not_performed')
    write_csv(directory,'validated_geographic_observations.csv',observations)
    write_csv(directory,'inverclyde_trends.csv',council)
    write_csv(directory,'scotland_trends.csv',national)
    write_csv(directory,'registered_scotland_comparisons.csv',compared)
    write_csv(directory,'published_five_year_rates.csv',rates)
    write_csv(directory,'published_rate_comparisons.csv',rate_compared)
    write_csv(directory,'annual_population_rates.csv',annual_rates)
    for name,value in [('geographic_evidence_hierarchy.json',hierarchy()),('data_quality_report.json',quality),
                       ('source_provenance.json',source),('research_findings.json',findings),('dashboard_data_contract.json',contract)]:
        write_json(directory,name,value)
    text=['# Geographic research findings — frozen 2024 NRS vintage','',
          f"Inverclyde: {latest['observed_value']} registered drug misuse deaths in 2024; {latest['annual_change']:+g} ({latest['annual_change_pct']:+.2f}%) from 2023.",
          f"Scotland (same registered measure): {national_latest['observed_value']}; {national_latest['annual_change_pct']:+.2f}% from 2023.",
          f"Inverclyde full-period high: {peaks['Inverclyde']['highest_count']} in {peaks['Inverclyde']['highest_years']}; low: {peaks['Inverclyde']['lowest_count']} in {peaks['Inverclyde']['lowest_years']}.",
          f"Inverclyde 2024 trailing 3/5-year means: {latest['rolling_3y_mean']:.2f} / {latest['rolling_5y_mean']:.2f}.",
          f"Non-overlapping 2010–2014 vs 2020–2024 annual means: {sum(early)/5:.1f} vs {sum(late)/5:.1f} ({pct:+.2f}%).",'',
          '## Verified annual counts','', '| Year | Inverclyde registered deaths | Scotland registered deaths |','| --- | ---: | ---: |']
    for row in compared:
        text.append(f"| {row['year']} | {row['inverclyde_deaths']} | {row['scotland_deaths']} |")
    last=rate_compared[-1]
    text.extend(['',f"NRS 2020–2024 published ASR: Inverclyde {last['inverclyde_rate']} (95% CI {last['inverclyde_lower95']}–{last['inverclyde_upper95']}); Scotland {last['scotland_rate']} ({last['scotland_lower95']}–{last['scotland_upper95']}) per 100,000, 2013 ESP.",
                 'These are five-year age-standardised source rates, not calculated annual crude rates. No compatible council denominator was found in the inspected local population files.',
                 '',*['- '+v for v in findings['limitations']],''])
    (directory/'RESEARCH_FINDINGS.md').write_text('\n'.join(text),encoding='utf-8')
    if preserve()!=before or any(sha(ROOT/path)!=expected for path,expected in inputs.items()):
        raise ValueError('Preserved research artifacts or raw inputs changed')
    code=list(HERE.glob('*.py'))+[HERE/'README.md',ROOT/'analysis/tests/test_phase6.py']
    write_json(directory,'run_manifest.json',dict(version='phase6-1.0.0',executed_at_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
               analysis_as_of='2026-11-10',input_hashes=inputs,protected_artifact_hashes=before,
               code_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in code if p.exists()},
               output_hashes={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file() and p.name!='run_manifest.json'},
               execution='Local only; deterministic non-timestamped outputs; no database/frontend/previous-output writes'))
    return findings


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir')
    result=run(parser.parse_args().output_dir)
    print(json.dumps(dict(latest_inverclyde=result['latest']['observed_value'],latest_scotland=result['matched_scotland_latest']['observed_value'],
                          extrema=result['extrema'],published_rates=result['latest_published_rate_comparison']),indent=2))
