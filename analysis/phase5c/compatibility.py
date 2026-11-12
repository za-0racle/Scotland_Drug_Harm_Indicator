"""Explicit contextual mappings; no latent population or substance equivalence."""
from datetime import date

ALIASES = {'Scotland national total': 'Scotland', 'Scotland': 'Scotland',
           'NHS Greater Glasgow & Clyde': 'NHS Greater Glasgow and Clyde',
           'NHS Greater Glasgow and Clyde': 'NHS Greater Glasgow and Clyde'}
SUBSTANCES = {'Opioids': 'opioids', 'Opioid': 'opioids', 'Benzodiazepine': 'benzodiazepines',
              'Benzodiazepines': 'benzodiazepines', 'All Benzodiazepines': 'benzodiazepines',
              'Street Benzodiazepines': 'street_benzodiazepines', 'Prescribable Benzodiazepines': 'prescribable_benzodiazepines',
              'Stimulants': 'stimulants', 'Stimulant': 'stimulants', 'Dissociatives': 'dissociatives',
              'Gabapentinoids': 'gabapentinoids', 'Gabapentin/Pregabalin': 'gabapentinoids'}


def geo(name):
    if name in ALIASES:
        return dict(name=ALIASES[name], boundary='country' if ALIASES[name]=='Scotland' else 'health_board')
    if name == 'Scotland forensic testing sample':
        return dict(name='Scotland', boundary='national_testing_sample')
    if name.startswith('NHS '):
        return dict(name=name, boundary='health_board')
    if ': ' in name:
        return dict(name=name, boundary='police_division')
    if name == 'Unknown':
        return dict(name=name, boundary='unknown')
    return dict(name=name, boundary='unresolved')


def compare(a, b):
    """Return dimensional decisions, including meaningful contextual comparisons."""
    ga, gb = geo(a['geography']), geo(b['geography'])
    if 'unknown' in (ga['boundary'],gb['boundary']):
        geography = 'unresolved'
    elif ga == gb:
        geography = 'exact'
    elif ga['name'] == gb['name'] == 'Scotland' and 'national_testing_sample' in (ga['boundary'],gb['boundary']):
        geography = 'national_sample_context_only'
    elif ga['boundary']=='unresolved' or gb['boundary']=='unresolved':
        geography = 'unresolved'
    else:
        geography = 'incompatible'
    sa, sb = a.get('substance_category'), b.get('substance_category')
    ma, mb = SUBSTANCES.get(sa), SUBSTANCES.get(sb)
    if not sa or not sb:
        substance = 'all_drug_context_only' if not sa and not sb else 'substance_vs_all_drug_context_only'
    elif ma and mb:
        substance = 'mapped_group' if ma == mb else 'incompatible'
    else:
        substance = 'unresolved'
    bounds = [a.get('period_start'),a.get('period_end'),b.get('period_start'),b.get('period_end')]
    for value in bounds:
        if value:
            date.fromisoformat(value)
    if all(bounds) and (bounds[0]>bounds[1] or bounds[2]>bounds[3]):
        raise ValueError('Reversed observation interval')
    if not all(bounds):
        temporal = 'unresolved'
    elif bounds[:2] == bounds[2:]:
        temporal = 'exact'
    elif max(bounds[0],bounds[2]) > min(bounds[1],bounds[3]):
        temporal = 'incompatible'
    elif (bounds[0] <= bounds[2] <= bounds[3] <= bounds[1]) or (bounds[2] <= bounds[0] <= bounds[1] <= bounds[3]):
        temporal = 'contained_context_only'
    else:
        temporal = 'partial_overlap_context_only'
    dependent = a['source_path'] == b['source_path'] or {a['dataset'],b['dataset']} == {'forensic_counts','frozen_forensic_shares'}
    independence = 'shared_source_not_independent' if dependent else 'distinct_collection_processes_shared_cases_unknown'
    measurement = 'different_measurements_context_only' if a['dataset'] != b['dataset'] else 'same_measurement'
    dates = [a.get('publication_date'),b.get('publication_date')]
    available = 'unknown' if not all(dates) else 'not_as_issued' if any(d > max(bounds[1] or '',bounds[3] or '') for d in dates) else 'publication_dates_only_not_vintage_verified'
    if dependent:
        status = 'incompatible'
        reason = 'Same underlying testing source is not independent corroboration'
    elif 'incompatible' in (geography,substance,temporal):
        status, reason = 'incompatible', 'Geography, substance or observation interval does not match'
    elif 'unresolved' in (geography,substance,temporal):
        status, reason = 'unresolved_mapping', 'Missing boundary, substance mapping or exact dates'
    elif geography == temporal == 'exact' and substance in ('mapped_group','all_drug_context_only') and measurement == 'same_measurement':
        status, reason = 'exact_match', 'Same scope and measurement; dependence still requires review'
    else:
        status, reason = 'compatible_contextual_evidence', 'Compare original states as context only; no equivalent population/exposure or prospective confirmation'
    return dict(status=status, geography=geography, substance=substance, temporal=temporal, measurement=measurement,
                independence=independence, historical_availability=available, reason=reason,
                shared_cases='Unknown; do not infer independence or causation')


def evidence(a, b, decision):
    if decision['status'] not in ('compatible_contextual_evidence','exact_match'):
        return 'no_compatible_cross_source_evidence'
    states = [a['signal_direction'],b['signal_direction']]
    if 'unavailable' in states:
        return 'compatible_context_states_unavailable'
    if states[0] == states[1] and states[0] in ('increase','decrease'):
        return 'supporting_contextual_signals_not_confirmation'
    if set(states) == {'increase','decrease'}:
        return 'opposing_contextual_signals_not_causal_conflict'
    if any(s in ('increase','decrease') for s in states):
        return 'single_signal_with_unflagged_context'
    return 'no_joint_detected_signal_not_no_harm'


def geographic_contract():
    result=[dict(scope=name, boundary=boundary, supported_indicators=indicators,
                 greenock_inference=False, population_rates='not_computed: compatible numerator/population-year/boundary join not verified',
                 dashboard_contract=dict(required=['scope_label','boundary_type','period_start','period_end','source_cutoff','measurement','limitations'],
                                         missing_state='No compatible local series available; wider-area context only'))
            for name,boundary,indicators in [
                ('Greenock','locality',[]), ('Inverclyde','council',[]),
                ('K: Renfrewshire and Inverclyde','police_division',['legacy quarterly suspected deaths']),
                ('NHS Greater Glasgow and Clyde','health_board',['weekly ambulance naloxone','monthly treatment urine detections']),
                ('Scotland','country',['legacy quarterly suspected deaths','weekly ambulance naloxone','national forensic sample context'])]]
    for record in result:
        record['historical_trends_supported']=bool(record['supported_indicators'])
        record['descriptive_comparisons']='Only matching boundary, measurement and period; no cross-boundary rates'
        record['surveillance_context']='Historical wider-area context only; no locality attribution'
        if record['scope']=='Inverclyde':
            record['available_unintegrated_asset']={'path':'datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx','sheet':'Table_C1',
                'verified_structure':'Inverclyde column; annual 2010–2024 registered drug misuse deaths, distinct from suspected deaths',
                'status':'Metadata readiness only; no counts imported, no rates or dashboard implemented'}
    return result
