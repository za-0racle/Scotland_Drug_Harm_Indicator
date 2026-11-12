// Pure transformations: stored observations and flags are never recomputed.
export const quarterIndex = (year, quarter) => Number(year) * 4 + Number(quarter) - 1;
export const quarterLabel = index => `${Math.floor(index / 4)} Q${index % 4 + 1}`;
export const isCusum = configuration => configuration?.method?.toUpperCase() === 'CUSUM';

export function chronological(rows, year = 'year', quarter = 'quarter') {
  return [...rows].sort((a, b) => quarterIndex(a[year], a[quarter]) - quarterIndex(b[year], b[quarter]));
}

export function filterYears(rows, start, end) {
  if (Number(start) > Number(end)) return [];
  return chronological(rows).filter(row => row.year >= Number(start) && row.year <= Number(end));
}

export function configurationResults(rows, id) {
  return chronological(rows.filter(row => String(row.configuration_id) === String(id)), 'observation_year', 'observation_quarter');
}

export function signals(rows) {
  return rows.filter(row => row.signal_flag === true);
}

export function summary(states) {
  const count = key => states[key]?.state === 'ready' ? states[key].rows.length : null;
  return {
    quarters: count('mortality'), results: count('results'), configurations: count('configurations'),
    signals: states.results?.state === 'ready' ? signals(states.results.rows).length : null,
  };
}

// Null slots represent absent quarters only. They never become observations,
// counts, interpolated values, or table rows; Chart.js leaves a visible gap.
export function timeline(rows, year = 'year', quarter = 'quarter') {
  const ordered = chronological(rows, year, quarter);
  if (!ordered.length) return [];
  const byQuarter = new Map(ordered.map(row => [quarterIndex(row[year], row[quarter]), row]));
  const first = quarterIndex(ordered[0][year], ordered[0][quarter]);
  const last = quarterIndex(ordered.at(-1)[year], ordered.at(-1)[quarter]);
  return Array.from({ length: last - first + 1 }, (_, i) => ({ label: quarterLabel(first + i), row: byQuarter.get(first + i) ?? null }));
}

export function mortalitySeries(rows) {
  const slots = timeline(rows);
  return { labels: slots.map(slot => slot.label), values: slots.map(slot => slot.row?.suspected_deaths ?? null) };
}

export function monitoringSeries(rows, configuration) {
  const slots = timeline(rows, 'observation_year', 'observation_quarter');
  const values = field => slots.map(slot => slot.row?.[field] ?? null);
  const series = isCusum(configuration)
    ? [{ label: 'Positive CUSUM', values: values('cusum_positive') }, { label: 'Negative CUSUM', values: values('cusum_negative') }, { label: 'Stored upper decision limit', values: values('upper_limit'), limit: true }]
    : [{ label: 'Stored EWMA statistic', values: values('statistic_value') }, { label: 'Stored upper limit', values: values('upper_limit'), limit: true }, { label: 'Stored lower limit', values: values('lower_limit'), limit: true }];
  series.push({ label: 'Recorded retrospective flag', values: slots.map(slot => slot.row?.signal_flag === true ? slot.row.statistic_value : null), flags: true });
  return { labels: slots.map(slot => slot.label), series };
}
