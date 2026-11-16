import io
import json
from urllib.parse import parse_qs,urlparse

import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app
from backend.repositories.supabase import DatabaseError,SupabaseRepository
from backend.services.platform import PlatformService


class Reply(io.BytesIO):
    def __init__(self,body,content_range):
        super().__init__(body)
        self.headers={'Content-Range':content_range}


def test_paginated_repository_reads_only_explicit_live_tables_and_validates_rows():
    seen=[]
    row={'week_beginning':'2024-01-01','reported_board':'NHS Ayrshire & Arran',
         'administrations':0,'moving_average':0.5,
         'source_dataset':'radar_sas_naloxone_weekly_by_board.csv'}
    def opener(request,timeout):
        seen.append((request,timeout))
        return Reply(json.dumps([row]).encode(),'0-0/1')
    repo=SupabaseRepository(Settings('https://test.supabase.co','sb_publishable_TEST'),opener)
    records,total=repo.read_page('naloxone_activity',0,1)
    assert records==[row] and total==1
    assert seen[0][1]==30 and request_query(seen[0][0])=={
        'select':['week_beginning,reported_board,administrations,moving_average,source_dataset'],
        'order':['week_beginning.asc,reported_board.asc'],'limit':['1'],'offset':['0']}
    with pytest.raises(DatabaseError):repo.read_page('radar_intelligence',0,10)

    def invalid(_request,timeout):return Reply(b'[{}]','*/1')
    with pytest.raises(DatabaseError,match='page window'):
        SupabaseRepository(repo.settings,invalid).read_page('naloxone_activity',0,1)

    bad={**row,'moving_average':float('inf')}
    def invalid_value(_request,timeout):return Reply(json.dumps([bad]).encode(),'0-0/1')
    with pytest.raises(DatabaseError,match='moving average'):
        SupabaseRepository(repo.settings,invalid_value).read_page('naloxone_activity',0,1)


def request_query(request):
    return parse_qs(urlparse(request.full_url).query)


class SnapshotDatabase:
    def __init__(self,rows):self.rows=rows
    def read(self,table):return []
    def read_page(self,table,offset,limit):
        rows=self.rows[table]
        return rows[offset:offset+limit],len(rows)


def test_live_naloxone_api_classifies_by_registry_and_keeps_source_zero_and_average():
    weekly=[]
    for label,value,average in [
        ('NHS Ayrshire & Arran',0,0.5),('Scotland',4,None),('Unknown',1,None)
    ]:
        weekly.append({'week_beginning':'2024-01-01','reported_board':label,
                       'administrations':value,'moving_average':average,
                       'source_dataset':'radar_sas_naloxone_weekly_by_board.csv'})
    sources=[{'dataset_name':'radar_sas_naloxone_weekly_by_board.csv','source_id':14,
              'source_sha256':'a'*64,'source_url':'https://example.test/source.csv',
              'publisher':'Public Health Scotland','notes':None}]
    client=TestClient(create_app(PlatformService(database=SnapshotDatabase({
        'naloxone_activity':weekly,'data_sources':sources,'geographic_areas':[]}))))
    response=client.get('/api/v1/database/v1/naloxone-activity?offset=0&limit=2')
    assert response.status_code==200
    body=response.json()
    assert body['total']==3 and len(body['data'])==2
    board,national=body['data']
    assert (board['geography_class'],board['administrations'],board['moving_average'])==('nhs_board',0,0.5)
    assert national['geography_class']=='national'
    assert national['geography_display']=='National Aggregate — Scotland'
    assert body['metadata']['source_id']==14 and body['metadata']['source_sha256']=='a'*64
    last=client.get('/api/v1/database/v1/naloxone-activity?offset=2&limit=2').json()
    assert last['data'][0]['geography_class']=='unknown'


def test_live_database_routes_validate_paging_return_empty_and_fail_closed():
    class EmptyDatabase(SnapshotDatabase):
        def __init__(self):super().__init__({'data_sources':[],'geographic_areas':[],'naloxone_activity':[]})
    client=TestClient(create_app(PlatformService(database=EmptyDatabase())))
    response=client.get('/api/v1/database/v1/geographic-areas')
    assert response.status_code==200 and response.json()['state']=='empty'
    assert client.get('/api/v1/database/v1/data-sources?limit=0').status_code==422
    assert client.get('/api/v1/database/v1/naloxone-activity?arbitrary_sql=select').status_code==422
    assert client.get('/api/v1/database/v1/radar-intelligence').status_code==404

    rows=[{'week_beginning':'2024-01-01','reported_board':'Unrecognized board',
           'administrations':2,'moving_average':None,
           'source_dataset':'radar_sas_naloxone_weekly_by_board.csv'}]
    sources=[{'dataset_name':'radar_sas_naloxone_weekly_by_board.csv','source_id':14,
              'source_sha256':'b'*64,'source_url':None,'publisher':'Public Health Scotland','notes':None}]
    invalid=TestClient(create_app(PlatformService(database=SnapshotDatabase({
        'naloxone_activity':rows,'data_sources':sources,'geographic_areas':[]}))))
    assert invalid.get('/api/v1/database/v1/naloxone-activity').status_code==503
