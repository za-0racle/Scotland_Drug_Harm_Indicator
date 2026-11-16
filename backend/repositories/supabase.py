import base64
import math
import json
import re
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlparse
from datetime import date
from backend.config import Settings

TABLES={
 'mortality_quarterly':('year,quarter,suspected_deaths','year.asc,quarter.asc'),
 'indicator_configurations':('configuration_id,indicator_name,configuration_label,method,baseline_description,rolling_window_quarters,lambda_value,limit_multiplier,lower_limit,upper_limit,cusum_k_sigma,cusum_h_sigma,notes','configuration_id.asc'),
 'indicator_results':('result_id,configuration_id,observation_year,observation_quarter,statistic_value,lower_limit,upper_limit,signal_flag,cusum_positive,cusum_negative,computation_reference','observation_year.asc,observation_quarter.asc,configuration_id.asc,result_id.asc')}

SNAPSHOT_TABLES={
 'data_sources':('dataset_name,publisher,source_url,source_sha256,notes,source_id','dataset_name.asc,source_id.asc'),
 'geographic_areas':('area_code,area_name,area_type,valid_from,valid_to,source_dataset','area_code.asc,valid_from.asc'),
 'naloxone_activity':('week_beginning,reported_board,administrations,moving_average,source_dataset','week_beginning.asc,reported_board.asc')}

READ_ONLY_TABLES={**TABLES,**SNAPSHOT_TABLES}
PAGED_TABLES=frozenset(SNAPSHOT_TABLES)


class DatabaseError(Exception):pass


class SupabaseRepository:
    def __init__(self,settings=None,opener=urlopen):self.settings=settings or Settings.load();self.opener=opener

    def _headers_and_url(self,table,columns,order,limit,offset):
        if table not in READ_ONLY_TABLES:raise DatabaseError('Table is outside reviewed read-only scope')
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
        query=urlencode(dict(select=columns,order=order,limit=limit,offset=offset))
        headers={'apikey':key,'Prefer':'count=exact','Accept':'application/json'}
        if not key.startswith('sb_publishable_'):headers['Authorization']='Bearer '+key
        return url.rstrip('/')+'/rest/v1/'+table+'?'+query,headers

    @staticmethod
    def _validate_page_rows(table,rows):
        def text(value):
            return isinstance(value,str) and bool(value.strip()) and len(value)<=1000

        for row in rows:
            if table=='data_sources':
                if not text(row.get('dataset_name')) or not isinstance(row.get('source_id'),int) or isinstance(row.get('source_id'),bool) or row['source_id']<1:
                    raise DatabaseError('Invalid source catalog record')
                if row.get('publisher') is not None and not text(row['publisher']):raise DatabaseError('Invalid source publisher')
                if row.get('source_url') is not None and (not text(row['source_url']) or any(ord(char)<32 for char in row['source_url'])):
                    raise DatabaseError('Invalid source URL')
                if not isinstance(row.get('source_sha256'),str) or not re.fullmatch(r'[0-9a-fA-F]{64}',row['source_sha256']):
                    raise DatabaseError('Invalid source checksum')
                if row.get('notes') is not None and not isinstance(row['notes'],str):raise DatabaseError('Invalid source notes')
            elif table=='geographic_areas':
                if not all(text(row.get(field)) for field in ('area_code','area_name','area_type','source_dataset')):
                    raise DatabaseError('Invalid geographic registry record')
                try:
                    start=date.fromisoformat(row['valid_from']) if row.get('valid_from') is not None else None
                    end=date.fromisoformat(row['valid_to']) if row.get('valid_to') is not None else None
                except (TypeError,ValueError):raise DatabaseError('Invalid geographic validity date') from None
                if row.get('valid_from') is None or start is None or (end is not None and end<start):
                    raise DatabaseError('Invalid geographic validity interval')
            elif table=='naloxone_activity':
                if not text(row.get('reported_board')) or not text(row.get('source_dataset')):
                    raise DatabaseError('Invalid naloxone source label')
                if not isinstance(row.get('administrations'),int) or isinstance(row.get('administrations'),bool) or row['administrations']<0:
                    raise DatabaseError('Invalid naloxone administration count')
                moving=row.get('moving_average')
                if moving is not None and (isinstance(moving,bool) or not isinstance(moving,(int,float)) or not math.isfinite(moving) or moving<0):
                    raise DatabaseError('Invalid source-reported naloxone moving average')
                try:week=date.fromisoformat(row.get('week_beginning',''))
                except (TypeError,ValueError):raise DatabaseError('Invalid naloxone reporting week') from None
                if week.weekday()!=0:raise DatabaseError('Naloxone reporting week must begin on Monday')

    def read_page(self,table,offset=0,limit=100):
        if table not in PAGED_TABLES:raise DatabaseError('Table is outside paginated read-only scope')
        if isinstance(offset,bool) or not isinstance(offset,int) or offset<0 or offset>1000000:
            raise DatabaseError('Invalid database page offset')
        if isinstance(limit,bool) or not isinstance(limit,int) or limit<1 or limit>1000:
            raise DatabaseError('Invalid database page size')
        columns,order=SNAPSHOT_TABLES[table]
        url,headers=self._headers_and_url(table,columns,order,limit,offset)
        try:
            with self.opener(Request(url,headers=headers),timeout=30) as response:
                data=json.load(response)
                content_range=response.headers.get('Content-Range','')
            if not isinstance(data,list) or any(not isinstance(row,dict) for row in data):
                raise DatabaseError('Malformed database response')
            match=re.fullmatch(r'(?:(\d+)-(\d+)|\*)/(\d+)',content_range)
            if not match:raise DatabaseError('Database page total is unavailable; complete pagination cannot be verified')
            total=int(match.group(3))
            expected=min(limit,max(total-offset,0))
            if len(data)!=expected:
                raise DatabaseError('Incomplete database page; returned rows do not match the exact count')
            if data and (match.group(1) is None or int(match.group(1))!=offset or int(match.group(2))!=offset+len(data)-1):
                raise DatabaseError('Database page window is inconsistent')
            self._validate_page_rows(table,data)
            return data,total
        except DatabaseError:raise
        except Exception:raise DatabaseError('Supabase read failed; check backend connectivity and approved RLS access') from None

    def read(self,table):
        if table not in READ_ONLY_TABLES:raise DatabaseError('Table is outside reviewed read-only scope')
        columns,order=READ_ONLY_TABLES[table];rows=[]
        try:
            for offset in range(0,10000,500):
                url,headers=self._headers_and_url(table,columns,order,500,offset)
                with self.opener(Request(url,headers=headers),timeout=12) as response:
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
