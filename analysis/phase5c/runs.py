"""Consecutive statistical observations, never inferred toxicity incidents."""
from collections import defaultdict


def group_runs(rows):
    grouped = defaultdict(list)
    seen = set()
    for r in rows:
        k = (r['dataset'], r['indicator_id'], r['geography'], r['period_basis'], r['method'], str(r['configuration']))
        identity = k + (int(r['ordinal']),)
        if identity in seen:
            raise ValueError('Duplicate run observation')
        seen.add(identity)
        if r['direction'] in ('increase', 'decrease'):
            grouped[k + (r['direction'],)].append(r)
    output = []
    for k, values in sorted(grouped.items()):
        sequences = []
        for r in sorted(values, key=lambda r: int(r['ordinal'])):
            if not sequences or int(r['ordinal']) != int(sequences[-1][-1]['ordinal']) + 1:
                sequences.append([])
            sequences[-1].append(r)
        for sequence in sequences:
            peak = max(sequence, key=lambda r: abs(r['deviation']))
            output.append(dict(dataset=k[0], indicator_id=k[1], geography=k[2], period_basis=k[3], method=k[4],
                               configuration=k[5], direction=k[6], start=sequence[0]['period'], end=sequence[-1]['period'],
                               duration_periods=len(sequence), classification='sustained_statistical_run' if len(sequence)>1 else 'isolated_flag',
                               peak_deviation=peak['deviation'], deviation_unit=peak['deviation_unit'], peak_period=peak['period'],
                               observation_ids=[r['observation_id'] for r in sequence], scientific_status='not_confirmed_toxicity_incident'))
    return output
