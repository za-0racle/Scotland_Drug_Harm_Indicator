// Only the three reviewed aggregate/model tables belong in this public reader.
export const datasets = {
  mortality: {
    table: 'mortality_quarterly',
    columns: 'year,quarter,suspected_deaths',
    order: ['year', 'quarter'],
  },
  configurations: {
    table: 'indicator_configurations',
    columns: 'configuration_id,indicator_name,configuration_label,method,baseline_description,rolling_window_quarters,lambda_value,limit_multiplier,lower_limit,upper_limit,cusum_k_sigma,cusum_h_sigma,notes',
    order: ['configuration_id'],
  },
  results: {
    table: 'indicator_results',
    columns: 'result_id,configuration_id,observation_year,observation_quarter,statistic_value,lower_limit,upper_limit,signal_flag,cusum_positive,cusum_negative,computation_reference,configuration:indicator_configurations!indicator_results_configuration_id_fkey(configuration_label)',
    order: ['observation_year', 'observation_quarter', 'configuration_id', 'result_id'],
  },
};

export async function readDataset(client, definition, pageSize = 500) {
  if (!Number.isInteger(pageSize) || pageSize < 1) throw new Error('Invalid page size.');
  const rows = [];
  for (let offset = 0; ; offset += pageSize) {
    let query = client.from(definition.table).select(definition.columns, { count: 'exact' });
    for (const column of definition.order) query = query.order(column, { ascending: true });
    const { data, error, count } = await query.range(offset, offset + pageSize - 1);
    if (error) throw new Error(`${definition.table}: ${error.message}${error.code ? ` (${error.code})` : ''}`);
    if (!Array.isArray(data)) throw new Error(`${definition.table}: invalid database response.`);
    rows.push(...data);
    // Count also handles a server page cap smaller than the requested range.
    if (count !== null && count !== undefined && rows.length >= count) break;
    if (data.length < pageSize) {
      if (count !== null && count !== undefined && rows.length < count) {
        throw new Error(`${definition.table}: incomplete response; server page limit is smaller than requested.`);
      }
      break;
    }
  }
  return rows;
}

export async function loadDataset(client, definition) {
  try {
    if (!client) throw new Error('Configure the Supabase URL and publishable key in .env.local.');
    const rows = await readDataset(client, definition);
    return { state: rows.length ? 'ready' : 'empty', rows };
  } catch (error) {
    return { state: 'error', rows: [], message: error.message };
  }
}

export function describeDataset(result) {
  if (result.state === 'loading') return 'Loading records…';
  if (result.state === 'error') return `Supabase error: ${result.message}`;
  if (result.state === 'empty') return '0 accessible records. The table may be empty or RLS may be withholding rows. Check the approved read policies and data availability.';
  const missingLabels = result.rows.filter(row => 'configuration' in row && !row.configuration?.configuration_label).length;
  return `${result.rows.length} records returned.${missingLabels ? ` ${missingLabels} configuration labels are unavailable; check configuration read access.` : ''}`;
}
