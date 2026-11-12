"""Execute versioned local analytical comparisons; never writes older outputs."""
import argparse
import csv
import hashlib
import json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

from analysis.phase5.run import protected_hashes
from analysis.phase5c.models import METHODS,predict
from analysis.phase5c.compatibility import compare,evidence,geographic_contract
from analysis.phase5c.runs import group_runs
from analysis.phase5c.sources import registry,gaps,official_review
from analysis.phase5c.foi import specification

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'analysis/phase5c'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preserve():
    result=protected_hashes()
    for path in (ROOT/'analysis/phase5').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            result[path.relative_to(ROOT).as_posix()]=sha(path)
    # Verify original Phase 5 saved artifacts against the existing manifest.
    old=json.loads((ROOT/'analysis/phase5/outputs/run_manifest.json').read_text())
    for name,expected in old['output_hashes'].items():
        assert sha(ROOT/'analysis/phase5/outputs'/name)==expected,name
    for name,expected in old['source_code_hashes'].items():
        assert sha(ROOT/name)==expected,name
    return result


def load():
    with (ROOT/'analysis/phase5/outputs/anomaly_results.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        identity='|'.join(r[k] for k in ('dataset','indicator_id','geography','period_basis','period'))
        r['observation_id']=hashlib.sha256(identity.encode()).hexdigest()[:20]
    assert len({r['observation_id'] for r in rows})==len(rows)
    return rows


def write_json(directory,name,value):
    (directory/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def write_csv(directory,name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (directory/name).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def model_comparison(rows):
    groups=defaultdict(dict)
    for r in rows:
        if r['unit'] in ('count','detection_count','incident_count'):
            k=(r['dataset'],r['indicator_id'],r['geography'])
            if int(r['ordinal']) in groups[k]:
                raise ValueError('Duplicate observation')
            groups[k][int(r['ordinal'])]=r
    output=[];diagnostics=[]
    for key,indexed in sorted(groups.items()):
        for index,row in sorted(indexed.items()):
            primary_window=int(row['window'])
            stride=52 if row['dataset']=='naloxone_weekly' else 12 if row['dataset']=='treatment_counts' else 4
            for method in METHODS:
                window=208 if method=='seasonal_gamma_poisson' and stride==52 else primary_window
                references=[indexed.get(i) for i in range(index-window,index)]
                base=dict(observation_id=row['observation_id'],dataset=key[0],indicator_id=key[1],geography=key[2],
                          period=row['period'],ordinal=index,period_basis=row['period_basis'],method=method,window=window,
                          observed_value=float(row['observed_value']) if row['observed_value'] else None,
                          reference_start=references[0]['period'] if references[0] else None,
                          reference_end=references[-1]['period'] if references[-1] else None,
                          source_path=row['source_path'],source_sha256=row['source_sha256'],
                          status='insufficient_data',notes='Incomplete prior history; no imputation',
                          interpretation='Retrospective conditional model comparison, no calibrated event-warning probability')
                if not row['observed_value']:
                    base.update(status='unavailable_observation',notes='Current value suppressed')
                elif not all(r and r['observed_value']!='' for r in references):
                    pass
                elif method=='trend_poisson' and stride==52:
                    base.update(status='not_applicable',notes='Weekly log-linear trend alone omitted pending seasonal/recording-break specification')
                else:
                    values=[float(r['observed_value']) for r in references]
                    result=predict(values,float(row['observed_value']),method,stride)
                    base.update(result)
                    diagnostics.append({k:base.get(k) for k in ('observation_id','method','window','reference_start','reference_end','mean','variance','dispersion','zero_fraction','poisson_expected_zero','lag1_correlation','seasonal_lag_correlation','half_window_mean_change','linear_slope','notes','status')})
                output.append(base)
    return output,diagnostics


def scores(results):
    grouped=defaultdict(list)
    for r in results:
        grouped[(r['dataset'],r['indicator_id'],r['geography'])].append(r)
    output=[]
    for key,rows in sorted(grouped.items()):
        eligible={m:{r['observation_id'] for r in rows if r['method']==m and r['status']=='ok'} for m in METHODS}
        participants=[m for m in METHODS if eligible[m]]
        common=set.intersection(*(eligible[m] for m in participants)) if participants else set()
        for method in METHODS:
            own=[r for r in rows if r['method']==method and r['status']=='ok']
            for scope,values in [('available_origins',own),('common_origins',[r for r in own if r['observation_id'] in common])]:
                row=dict(dataset=key[0],indicator_id=key[1],geography=key[2],method=method,evaluation_scope=scope,
                         evaluated=len(values),available_origins=len(own),common_participants=','.join(participants),
                         selection='No model automatically selected; descriptive conditional distribution comparison')
                if values:
                    row.update(mae=float(np.mean([abs(r['error']) for r in values])),
                               rmse=float(np.sqrt(np.mean([r['error']**2 for r in values]))),
                               coverage95=float(np.mean([r['covered95'] for r in values])),coverage99=float(np.mean([r['covered99'] for r in values])),
                               mean_negative_log_score=float(np.mean([r['negative_log_score'] for r in values])),
                               mean_interval_score95=float(np.mean([r['interval_score95'] for r in values])),
                               mean_width95=float(np.mean([r['upper95']-r['lower95'] for r in values])),
                               signals99=sum(r['signal'] for r in values),signal_frequency99=float(np.mean([r['signal'] for r in values])))
                output.append(row)
    return output


def candidates(rows):
    national_m=[r for r in rows if r['dataset']=='mortality_quarterly' and r['geography']=='Scotland national total']
    national_n=[r for r in rows if r['dataset']=='naloxone_weekly' and r['geography']=='Scotland']
    forensic=[r for r in rows if r['dataset']=='forensic_counts']
    shares=[r for r in rows if r['dataset']=='frozen_forensic_shares']
    treatment=[r for r in rows if r['dataset']=='treatment_counts']
    assist=[r for r in rows if r['dataset']=='assist_percentages']
    pairs=[]
    for m in national_m:
        for other in forensic+national_n:
            if other['period_start'] <= m['period_end'] and other['period_end'] >= m['period_start']:
                pairs.append((m,other))
    for f in forensic:
        for other in shares+treatment:
            if other['period_start'] <= f['period_end'] and other['period_end'] >= f['period_start']:
                pairs.append((f,other))
        # Study labels cannot be aligned to quarters; preserve actual unresolved candidates once per final forensic period.
        if f['period']=='2026 Q1':
            for other in assist:
                if other['period'].startswith('Q15 '):
                    pairs.append((f,other))
    return pairs


def integrate(rows,results):
    enhanced={(r['observation_id'],r['method']):r for r in results}
    output=[];assessments=[]
    for a,b in candidates(rows):
        decision=compare(a,b)
        cid=a['observation_id']+':'+b['observation_id']
        rec=dict(comparison_id=cid,left_observation_id=a['observation_id'],right_observation_id=b['observation_id'],
                 left_dataset=a['dataset'],right_dataset=b['dataset'],left_indicator=a['indicator_id'],right_indicator=b['indicator_id'],
                 left_geography=a['geography'],right_geography=b['geography'],left_period=a['period'],right_period=b['period'],
                 left_state=a['signal_direction'],right_state=b['signal_direction'],**decision)
        output.append(rec)
        for method in ('phase5_robust','nb2_moments'):
            if method=='phase5_robust':
                aa,bb=a,b
            else:
                av,bv=enhanced.get((a['observation_id'],method)),enhanced.get((b['observation_id'],method))
                aa=dict(a,signal_direction=av.get('direction','unavailable') if av else 'unavailable')
                bb=dict(b,signal_direction=bv.get('direction','unavailable') if bv else 'unavailable')
            assessments.append(dict(comparison_id=cid,method=method,classification=evidence(aa,bb,decision),
                                    left_state=aa['signal_direction'],right_state=bb['signal_direction'],
                                    observation_ids=[a['observation_id'],b['observation_id']],
                                    retrospective_only=True,current_threat='not_assessed',
                                    limitation='Contextual direction comparison only; shared cases, exposure and historical publication availability unresolved'))
    assert len({r['comparison_id'] for r in output})==len(output)
    return output,assessments


def run(directory=None):
    before=preserve()
    directory=Path(directory or HERE/'outputs').resolve()
    if directory != HERE/'outputs' and not any(p.endswith('.local') for p in directory.parts):
        raise ValueError('Use phase5c/outputs or .local scratch')
    directory.mkdir(parents=True,exist_ok=True)
    rows=load();models,diagnostic=model_comparison(rows);metrics=scores(models)
    comparisons,assessments=integrate(rows,models)
    run_rows=[]
    for r in rows:
        run_rows.append(dict(r,method='phase5_robust',configuration='original_window='+r['window']+';k=3',
                             direction=r['signal_direction'],deviation=float(r['robust_score']) if r.get('robust_score') else 0,
                             deviation_unit='robust_scale_units'))
    original={r['observation_id']:r for r in rows}
    for r in models:
        if r['status']=='ok':
            parent=original[r['observation_id']]
            run_rows.append(dict(parent,method=r['method'],configuration='window='+str(r['window'])+';interval=99',direction=r['direction'],
                                 deviation=r['error'],deviation_unit='observed_minus_predictive_mean_count'))
    runs=group_runs(run_rows)
    lookup={(r['observation_id'],r['method']):r for r in models}
    sensitivity=[]
    for r in rows:
        if r['unit'] not in ('count','detection_count','incident_count'):
            continue
        for method in METHODS:
            m=lookup[(r['observation_id'],method)]
            sensitivity.append(dict(observation_id=r['observation_id'],dataset=r['dataset'],indicator_id=r['indicator_id'],geography=r['geography'],period=r['period'],
                                    baseline_phase5_state=r['signal_direction'],enhanced_method=method,status=m['status'],
                                    enhanced_state=m.get('direction','unavailable'),window=m['window'],
                                    agreement=r['signal_direction']==m.get('direction') if r['signal_direction']!='unavailable' and m['status']=='ok' else None,
                                    limit_comparability='Phase5 k=3 robust bounds vs model 99% discrete predictive bounds; unequal nominal calibration'))
    zero_review=[]
    for r in rows:
        if r['dataset']=='naloxone_weekly' and r['geography']=='Unknown' and r['classification']=='statistically_unusual_observation':
            zero_review.append(dict(observation_id=r['observation_id'],period=r['period'],observed=r['observed_value'],phase5_median=r['baseline_estimate'],
                                    phase5_bounds=[r['lower_threshold'],r['upper_threshold']],
                                    models=[lookup[(r['observation_id'],m)] for m in METHODS],geographic_interpretation='Unknown assignment, never a hotspot'))
    write_csv(directory,'enhanced_model_results.csv',models)
    write_csv(directory,'model_evaluation_metrics.csv',metrics)
    write_csv(directory,'statistical_diagnostics.csv',diagnostic)
    write_csv(directory,'robustness_comparisons.csv',sensitivity)
    for name,value in [('source_compatibility_registry.json',registry(rows)),('cross_source_candidates.json',comparisons),
                       ('cross_source_evidence.json',assessments),('signal_runs.json',runs),('source_gap_register.json',gaps()),
                       ('geographic_evidence.json',geographic_contract()),('foi_staging_specification.json',specification()),
                       ('zero_baseline_review.json',zero_review),('official_source_review.json',official_review())]:
        write_json(directory,name,value)
    # Index links every observation to original source and the unchanged Phase 5 record.
    write_csv(directory,'observation_index.csv',[{k:r.get(k) for k in ('observation_id','dataset','indicator_id','substance_category','geography','period','period_basis','ordinal','observed_value','unit','source_path','source_sha256','source_url','publication_date','source_data_cutoff')} for r in rows])
    summary=dict(observations=len(rows),original_primary_flags=sum(r['classification']=='statistically_unusual_observation' for r in rows),
                 model_statuses={m:dict(Counter(r['status'] for r in models if r['method']==m)) for m in METHODS},
                 model_signals={m:sum(r.get('signal',False) for r in models if r['method']==m) for m in METHODS},
                 cross_source_candidates=len(comparisons),compatibility=dict(Counter(r['status'] for r in comparisons)),
                 evidence_by_method={m:dict(Counter(r['classification'] for r in assessments if r['method']==m)) for m in ('phase5_robust','nb2_moments')},
                 original_runs=sum(r['method']=='phase5_robust' for r in runs),
                 sustained_original_runs=[r for r in runs if r['method']=='phase5_robust' and r['duration_periods']>1],
                 foi='pending; no real records staged, external metrics unavailable',future_forecasts='none issued',
                 interpretation='Retrospective exploratory comparison, no automatic method choice or operational warning validation')
    write_json(directory,'summary.json',summary)
    auxiliary=['datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx',
               'datasets/Group3_Item2_Data/ndrdd_data_tables_2021-2022.xlsx',
               'datasets/Group3_Item2_Data/nhs_scotland_population_estimates_hb2019.csv',
               'datasets/Additional_Group3_Item2_Data/treatment_group_sdmd_council.csv',
               'datasets/Group3_Item2_Data/sas_foi_215-26_naloxone.xls']
    write_json(directory,'local_source_inventory.json',dict(reviewed_assets={name:sha(ROOT/name) for name in auxiliary},
               findings=['NRS Table_C1 has annual registered drug misuse deaths and an Inverclyde column; no council counts imported',
                         'Health-board population file covers 1981–2025, not a verified police-division denominator',
                         'SDMD NumberAssessed is not a urine-test denominator',
                         'Naloxone FOI .xls is binary OLE format; not parsed by the existing openpyxl environment',
                         'NDRDD historical workbook is not an ASSIST study denominator source'],
               scope='Metadata inspection only; these assets are not additional model observations'))
    assert preserve()==before,'Previous artifacts changed'
    write_json(directory,'run_manifest.json',dict(version='phase5c-1.0.0',executed_at_utc=datetime.now(timezone.utc).isoformat(),
               analysis_as_of='2026-11-10',protected_artifact_hashes=before,
               code_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(HERE.glob('*.py'))},
               supporting_code_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE/'README.md',ROOT/'analysis/tests/test_phase5c.py'] if p.exists()},
               output_hashes={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file() and p.name!='run_manifest.json'},
               limitations='Execution timestamp varies; other outputs deterministic; no source-vintage or external-event validation'))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir')
    print(json.dumps(run(parser.parse_args().output_dir),indent=2))
