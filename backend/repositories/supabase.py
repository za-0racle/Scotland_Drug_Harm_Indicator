import base64
import json
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlparse
from backend.config import Settings

TABLES={
 'mortality_quarterly':('year,quarter,suspected_deaths','year.asc,quarter.asc'),
 'indicator_configurations':('configuration_id,indicator_name,configuration_label,method,baseline_description,rolling_window_quarters,lambda_value,limit_multiplier,lower_limit,upper_limit,cusum_k_sigma,cusum_h_sigma,notes','configuration_id.asc'),
 'indicator_results':('result_id,configuration_id,observation_year,observation_quarter,statistic_value,lower_limit,upper_limit,signal_flag,cusum_positive,cusum_negative,computation_reference','observation_year.asc,observation_quarter.asc,configuration_id.asc,result_id.asc')}


class DatabaseError(Exception):pass


class SupabaseRepository:
    def __init__(self,settings=None,opener=urlopen):self.settings=settings or Settings.load();self.opener=opener

    def read(self,table):
        if table not in TABLES:raise DatabaseError('Table is outside reviewed read-only scope')
        url,key=self.settings.supabase_url,self.settings.supabase_key
        if not url or not key:raise DatabaseError('Backend Supabase URL/publishable key is not configured')
        if urlparse(url).scheme!='https' or not urlparse(url).hostname or not urlparse(url).hostname.endswith('.supabase.co'):
            raise DatabaseError('Invalid Supabase project URL')
        if key.startswith('sb_secret_'):raise DatabaseError('A publishable/anon credential is required')
        if key.count('.')==2:
            try:
                role=json.loads(base64.urlsafe_b64decode(key.split('.')[1]+'==='))['role']
                if role!='anon':raise DatabaseError('Only anon access is permitted')
            except (ValueError,KeyError):raise DatabaseError('Invalid anon credential') from None
        columns,order=TABLES[table];rows=[]
        try:
            for offset in range(0,10000,500):
                query=urlencode(dict(select=columns,order=order,limit=500,offset=offset))
                headers={'apikey':key,'Prefer':'count=exact','Accept':'application/json'}
                if not key.startswith('sb_publishable_'):headers['Authorization']='Bearer '+key
                with self.opener(Request(url.rstrip('/')+'/rest/v1/'+table+'?'+query,headers=headers),timeout=12) as response:
                    data=json.load(response)
                    content_range=response.headers.get('Content-Range','')
                    total=int(content_range.rsplit('/',1)[1]) if '/' in content_range and content_range.rsplit('/',1)[1].isdigit() else None
                if not isinstance(data,list) or any(not isinstance(r,dict) for r in data):raise DatabaseError('Malformed database response')
                rows.extend(data)
                if total is not None and len(rows)>=total:return rows
                if len(data)<500:
                    if total is not None and len(rows)<total:raise DatabaseError('Incomplete database response; server page cap differs from request')
                    return rows
            raise DatabaseError('Database result exceeds bounded read scope')
        except DatabaseError:raise
        except Exception:raise DatabaseError('Supabase read failed; check backend connectivity and approved RLS access') from None
