"""Synthetic fixtures below are labelled test data, never real alert records."""
import json
import math
from pathlib import Path

import pytest

from analysis.phase5c.models import distribution,diagnostics,predict
from analysis.phase5c.compatibility import compare,evidence,geo,geographic_contract
from analysis.phase5c.runs import group_runs
from analysis.phase5c.foi import validate,stage,FIELDS
from analysis.phase5c.run import run,load,model_comparison,preserve


def observation(**changes):
    row=dict(dataset='mortality_quarterly',indicator_id='test_counts',geography='Scotland national total',
             source_path='test_source_A',substance_category='',period_start='2024-01-01',period_end='2024-03-31',
             publication_date='',signal_direction='increase')
    return dict(row,**changes)


def test_actual_sources_allow_context_without_equating_measurements():
    a=observation()
    b=observation(dataset='naloxone_weekly',source_path='test_source_B',geography='Scotland',period_start='2024-02-05',period_end='2024-02-11')
    result=compare(a,b)
    assert result['status']=='compatible_contextual_evidence'
    assert result['temporal']=='contained_context_only'
    assert result['measurement']=='different_measurements_context_only'
    assert result['historical_availability']=='unknown'
    assert evidence(a,b,result)=='supporting_contextual_signals_not_confirmation'
    assert evidence(a,dict(b,signal_direction='decrease'),result)=='opposing_contextual_signals_not_causal_conflict'
    assert evidence(a,dict(b,signal_direction='none'),result)=='single_signal_with_unflagged_context'
    assert evidence(a,dict(b,signal_direction='unavailable'),result)=='compatible_context_states_unavailable'
    assert evidence(dict(a,signal_direction='none'),dict(b,signal_direction='none'),result)=='no_joint_detected_signal_not_no_harm'


def test_geography_and_substance_mapping_do_not_infer_local_drugs():
    assert geo('Scotland')==geo('Scotland national total')
    assert geo('NHS Greater Glasgow & Clyde')==geo('NHS Greater Glasgow and Clyde')
    a=observation(geography='K: Renfrewshire and Inverclyde')
    b=observation(dataset='forensic_counts',source_path='B',geography='Scotland forensic testing sample',substance_category='Opioids')
    assert compare(a,b)['status']=='incompatible'
    assert compare(observation(),b)['substance']=='substance_vs_all_drug_context_only'
    assert compare(dict(a,geography='Unknown'),b)['status']=='unresolved_mapping'
    assert compare(dict(a,substance_category='Stimulants'),dict(b,geography=a['geography']))['substance']=='incompatible'
    assert compare(dict(a,substance_category='Opioids'),dict(b,geography=a['geography']))['substance']=='mapped_group'
    assert compare(dict(a,substance_category='Opioids (excluding treatment opioids)'),dict(b,geography=a['geography']))['status']=='unresolved_mapping'


def test_dependence_dates_and_historical_availability():
    a=observation(dataset='forensic_counts')
    b=observation(dataset='frozen_forensic_shares',source_path='another_source')
    assert compare(a,b)['independence']=='shared_source_not_independent'
    assert evidence(a,b,compare(a,b))=='no_compatible_cross_source_evidence'
    b=observation(source_path='B',publication_date='2026-01-01')
    assert compare(dict(a,publication_date='2026-01-01'),b)['historical_availability']=='not_as_issued'
    assert compare(a,dict(b,period_start='2025-01-01',period_end='2025-03-31'))['temporal']=='incompatible'
    assert compare(a,dict(b,period_start=''))['temporal']=='unresolved'
    assert compare(a,dict(b,period_start='2024-03-01',period_end='2024-04-30'))['temporal']=='partial_overlap_context_only'
    with pytest.raises(ValueError):
        compare(a,dict(b,period_end='2023-01-01'))


def test_gamma_poisson_includes_rate_uncertainty_and_valid_zero_baseline():
    dist,notes,_=distribution([0]*104,'gamma_poisson',52)
    assert dist.mean()==pytest.approx(.5/104.5)
    assert dist.var()>dist.mean()
    assert math.isfinite(predict([0]*104,4,'gamma_poisson',52)['negative_log_score'])
    assert predict([0]*104,4,'nb2_moments',52)['status']=='insufficient_data'
    assert 'posterior predictive' in notes
    result=predict([2,3,2,3,2,3]*3,2,'nb2_moments',12)
    assert 'Poisson limiting' in result['notes']


def test_overdispersion_and_prior_only_diagnostics():
    result=diagnostics([0,0,0,20]*4,4)
    assert result['dispersion']>1.5 and result['zero_fraction']==.75
    assert result['seasonal_lag_correlation']==pytest.approx(1)
    assert predict([0,0,0,20]*4,5,'nb2_moments',4)['status']=='ok'
    with pytest.raises(ValueError):
        diagnostics([1,-1])
    assert predict([2]*18,2,'seasonal_gamma_poisson',12)['status']=='insufficient_data'
    assert predict([2]*104,2,'seasonal_gamma_poisson',52)['status']=='insufficient_data'
    assert predict([2]*208,2,'seasonal_gamma_poisson',52)['status']=='ok'
    r=predict([1,2,3,4]*4,4,'seasonal_gamma_poisson',4)
    # Next period phase is zero: only four prior values of one enter this posterior.
    assert r['predicted']==pytest.approx(4.5/4.5)


def test_distribution_boundaries_and_scores():
    result=predict([10]*16,10,'gamma_poisson',4)
    assert result['lower99']<=result['lower95']<=10<=result['upper95']<=result['upper99']
    assert not result['signal'] and result['interval_score95']==result['upper95']-result['lower95']
    assert predict([10]*16,int(result['upper99']),'gamma_poisson',4)['direction']=='none'
    assert predict([10]*16,int(result['upper99'])+1,'gamma_poisson',4)['direction']=='increase'


def test_model_pipeline_prevents_future_leakage_and_missing_history():
    rows=[]
    for i in range(18):
        rows.append(dict(observation(),unit='count',period=str(i),ordinal=str(i),window='16',observed_value=str(10+i%3),
                         observation_id=str(i),source_sha256='test_only',period_basis='calendar_quarter'))
    before,_=model_comparison(rows[:17])
    after,_=model_comparison(rows)
    assert before==after[:len(before)]
    original=[r for r in before if r['observation_id']=='16' and r['method']=='gamma_poisson'][0]
    changed=[dict(r) for r in rows[:17]];changed[-1]['observed_value']='1000'
    amended,_=model_comparison(changed)
    amended=[r for r in amended if r['observation_id']=='16' and r['method']=='gamma_poisson'][0]
    assert amended['predicted']==original['predicted']
    assert amended['reference_end']=='15'
    changed[5]['observed_value']=''
    missing,_=model_comparison(changed)
    assert next(r for r in missing if r['observation_id']=='16' and r['method']=='gamma_poisson')['status']=='insufficient_data'


def test_runs_keep_sources_direction_configuration_and_gaps_separate():
    def r(i,**change):
        return dict(dict(dataset='fixture',indicator_id='drug',geography='Area A',period_basis='quarter',method='test',
                         configuration='test only',direction='increase',ordinal=i,period=str(i),deviation=i,
                         deviation_unit='count',observation_id=str(i)),**change)
    runs=group_runs([r(1),r(2),r(4),r(5,direction='decrease'),r(6,geography='Area B')])
    assert sorted(row['duration_periods'] for row in runs)==[1,1,1,2]
    sustained=next(row for row in runs if row['duration_periods']==2)
    assert sustained['observation_ids']==['1','2'] and sustained['peak_period']=='2'
    with pytest.raises(ValueError):
        group_runs([r(1),r(1)])


def foi_fixture():
    # SYNTHETIC TEST DATA; not an actual PHS alert.
    record={field:None for field in FIELDS}
    record.update(issuer='SYNTHETIC TEST ISSUER',official_alert_id='SYNTHETIC-001',issue_date='2024-01-02',
                  publication_date='2024-01-03',substances=['TEST SUBSTANCE'],geographic_scope={'name':'TEST AREA','boundary':'test'},
                  date_precision='day',alert_category='SYNTHETIC TEST',description='SYNTHETIC TEST DATA ONLY',source_locator='fixture row 1',
                  revision_status='original',withdrawal_status='unknown',record_version='1',
                  missingness_notes={key:'Not supplied in synthetic fixture' for key in ('event_date_start','event_date_end','detection_date')})
    return dict(response=dict(request_reference='SYNTHETIC TEST',received_date='2026-11-10',source_sha256='a'*64,
                              completeness='unknown',coverage={},limitations=['SYNTHETIC TEST DATA ONLY']),records=[record])


def test_foi_accepts_structural_fixture_without_opening_metric_gate(tmp_path):
    result=validate(foi_fixture())
    assert not result['metadata_issues'] and not result['records'][0]['issues']
    assert not result['external_validation_eligible'] and not result['public_export_approved']
    assert validate({'response':foi_fixture()['response'],'records':[]})['negative_labels'].startswith('Missing records')
    p=tmp_path/'synthetic_test_input.json';out=tmp_path/'synthetic_test_staged.json'
    p.write_text(json.dumps(foi_fixture()))
    stage(p,out)
    assert out.exists()
    with pytest.raises(ValueError):
        stage(p,out)
    with pytest.raises(ValueError):
        stage(p,p)


def test_foi_quarantines_ambiguity_duplicate_versions_and_revisions():
    p=foi_fixture();p['records'][0]['issue_date']='2024-01';p['records']*=2
    result=validate(p)
    assert all(r['review_status']=='quarantined' for r in result['records'])
    assert 'Duplicate alert version' in result['records'][1]['issues']
    p=foi_fixture();p['records'][0]['revision_status']='revised'
    assert any('parent' in issue for issue in validate(p)['records'][0]['issues'])
    with pytest.raises(ValueError):
        validate([])
    assert validate({'records':[None]})['rejected_records']
    assert validate({'records':[]})['metadata_issues']


def test_geographic_contract_preserves_missing_greenock_and_registered_distinction():
    metadata={r['scope']:r for r in geographic_contract()}
    assert not metadata['Greenock']['supported_indicators']
    assert not any(r['greenock_inference'] for r in metadata.values())
    assert metadata['Inverclyde']['available_unintegrated_asset']['sheet']=='Table_C1'
    assert all(r['population_rates'].startswith('not_computed') for r in metadata.values())


def test_full_outputs_reproduce_preserving_previous_phases(tmp_path):
    before=preserve()
    one,two=tmp_path/'one',tmp_path/'two'
    first=run(one);second=run(two)
    assert first==second
    assert first['observations']==8034 and first['original_primary_flags']==47
    assert first['original_runs']==44
    assert first['compatibility']['compatible_contextual_evidence']>0
    for path in one.iterdir():
        if path.name!='run_manifest.json':
            assert path.read_bytes()==(two/path.name).read_bytes(),path.name
    assert before==preserve()
    evidence=json.loads((one/'cross_source_evidence.json').read_text())
    assert all(len(r['observation_ids'])==2 for r in evidence)
    assert all(r['current_threat']=='not_assessed' for r in evidence)
