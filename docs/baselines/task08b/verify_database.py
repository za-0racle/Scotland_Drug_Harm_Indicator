"""Read approved tables and advertised metadata using existing anon credentials.
Never records credentials, project URLs, raw error bodies or database row values.
"""
import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from backend.config import Settings
from backend.repositories.supabase import SupabaseRepository, TABLES
from capture_baseline import save, digest

EXPECTED = ['data_sources','mortality_quarterly','forensic_toxicology','assist_toxicology',
            'radar_intelligence','radar_alerts','naloxone_activity','population_estimates',
            'geographic_areas','indicator_configurations','indicator_results']

if __name__ == '__main__':
    settings = Settings.load()
    result = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(), credential_scope='existing publishable/anon only',
                  tables={}, metadata={}, limitations=['PostgREST visibility is not a complete database catalog.',
                  'Successful reads do not prove policy definitions, keys, indexes or constraints.'])
    repository = SupabaseRepository(settings)
    for table in EXPECTED:
        item = dict(existence='unverified', columns='unverified', primary_keys='unverified', foreign_keys='unverified',
                    unique_constraints='unverified', indexes='unverified', read_policy_definitions='unverified')
        if table in TABLES:
            try:
                rows = repository.read(table)
                keys = {'mortality_quarterly':['year','quarter'], 'indicator_configurations':['configuration_id'],
                        'indicator_results':['configuration_id','observation_year','observation_quarter']}[table]
                item.update(existence='verified accessible through read-only PostgREST', records=len(rows),
                            projected_columns=TABLES[table][0].split(','), ordered_value_fingerprint=digest(rows),
                            observed_types={k:sorted({type(r.get(k)).__name__ for r in rows}) for k in TABLES[table][0].split(',')},
                            candidate_key=keys, candidate_key_duplicates=len(rows)-len({digest([r.get(k) for k in keys]) for r in rows}),
                            access='SELECT succeeded; policy definition unverified')
                if table == 'indicator_configurations':
                    item['configuration_identities'] = [{k:r.get(k) for k in TABLES[table][0].split(',') if k != 'notes'} for r in rows]
                if table == 'indicator_results':
                    item['configuration_ids'] = sorted({r['configuration_id'] for r in rows})
                    item['signal_count'] = sum(r.get('signal_flag') is True for r in rows)
            except Exception as error:
                item.update(access='read unavailable', error_type=type(error).__name__)
        result['tables'][table] = item
    if settings.supabase_url and settings.supabase_key:
        headers = {'apikey':settings.supabase_key, 'Accept':'application/openapi+json'}
        if not settings.supabase_key.startswith('sb_publishable_'): headers['Authorization']='Bearer '+settings.supabase_key
        # SupabaseRepository above enforces the permitted credential and URL scope.
        if any(x.get('records') is not None for x in result['tables'].values()):
            try:
                with urlopen(Request(settings.supabase_url.rstrip('/')+'/rest/v1/', headers=headers), timeout=12) as response:
                    document=json.load(response)
                result['metadata']['status']='OpenAPI received'
                result['metadata']['expected_table_definitions']={k:document.get('definitions',{}).get(k) for k in EXPECTED}
                result['metadata']['expected_table_paths']=[k for k in document.get('paths',{}) if k.lstrip('/') in EXPECTED]
            except HTTPError as error: result['metadata']=dict(status='unavailable', http_status=error.code)
            except (URLError,TimeoutError,ValueError) as error: result['metadata']=dict(status='unavailable', error_type=type(error).__name__)
    save('database-verification.json', result)
    print(json.dumps(dict(tables={k:dict(existence=v['existence'], records=v.get('records')) for k,v in result['tables'].items()},metadata=result['metadata'].get('status'))))
