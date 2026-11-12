import csv
import io
import json
import logging
from typing import Annotated,Literal
from fastapi import FastAPI,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,Response
from backend.config import Settings
from backend.schemas import Envelope,Filters
from backend.services.platform import PlatformService,QueryError
from backend.repositories.artifacts import ArtifactError,CATALOG
from backend.repositories.supabase import DatabaseError

logger=logging.getLogger('research_api')


def create_app(service=None,settings=None):
    app=FastAPI(title='Scotland Drug Harm Intelligence — research API',version='1.0.0')
    app.state.service=service or PlatformService();settings=settings or Settings.load()
    app.add_middleware(CORSMiddleware,allow_origins=list(settings.origins),allow_methods=['GET'],allow_headers=['Accept','Content-Type'],allow_credentials=False)

    @app.exception_handler(QueryError)
    async def query_error(request,error):return JSONResponse(status_code=422,content=dict(state='error',kind='unavailable_evidence',data=[],total=0,message=str(error),metadata={}))

    @app.exception_handler(DatabaseError)
    async def database_error(request,error):return JSONResponse(status_code=503,content=dict(state='error',kind='database_observation',data=[],total=0,message=str(error),metadata={}))

    @app.exception_handler(ArtifactError)
    async def artifact_error(request,error):return JSONResponse(status_code=503,content=dict(state='unavailable',kind='unavailable_evidence',data=[],total=0,message='Verified analytical resource unavailable; check server artifact integrity',metadata={}))

    @app.exception_handler(Exception)
    async def unexpected(request,error):
        logger.error('Research API request failed: %s',type(error).__name__)
        return JSONResponse(status_code=500,content=dict(state='error',kind='unavailable_evidence',data=[],total=0,message='Request could not be completed safely',metadata={}))

    @app.get('/api/v1/health',response_model=Envelope)
    def health():return Envelope(state='ready',kind='metadata',data=[dict(api='ok',database='checked separately by overview; not implied healthy',research_prototype=True)],total=1)

    @app.get('/api/v1/overview',response_model=Envelope)
    def overview():return app.state.service.overview()

    @app.get('/api/v1/geographies',response_model=Envelope)
    def geographies():
        rows=list(app.state.service.registry.values());return Envelope(state='ready',kind='metadata',data=rows,total=len(rows),limit=len(rows))

    @app.get('/api/v1/indicators',response_model=Envelope)
    def indicators():
        found={}
        for resource in ('mortality_trends','forensic','assist','treatment','naloxone','annual'):
            rows,_=app.state.service.artifacts.load(resource)
            for r in rows:
                key=r['indicator_id'];found.setdefault(key,dict(indicator_id=key,resource=resource,unit=r.get('unit'),period_basis=r.get('period_basis'),categories=set()))
                category=r.get('substance_category') or key.partition(':')[2]
                if category:found[key]['categories'].add(category)
        items=[dict(r,categories=sorted(r['categories'])) for r in found.values()]
        return Envelope(state='ready',kind='metadata',data=items,total=len(items))

    @app.get('/api/v1/geographies/{geography_id}',response_model=Envelope)
    def area(geography_id:str):return Envelope(state='ready',kind='metadata',data=[app.state.service.area(geography_id)],total=1)

    @app.get('/api/v1/geographies/{geography_id}/{section}',response_model=Envelope)
    def area_data(geography_id:str,section:Literal['indicators','trends','anomalies','evidence','comparisons'],filters:Annotated[Filters,Query()]):
        return app.state.service.geography_data(geography_id,section,filters)

    @app.get('/api/v1/mortality/quarterly',response_model=Envelope)
    def mortality(filters:Annotated[Filters,Query()]):return app.state.service.db('mortality_quarterly',filters)

    @app.get('/api/v1/monitoring/configurations',response_model=Envelope)
    def configurations(filters:Annotated[Filters,Query()]):return app.state.service.db('indicator_configurations',filters)

    @app.get('/api/v1/monitoring/results',response_model=Envelope)
    def monitoring(filters:Annotated[Filters,Query()]):return app.state.service.db('indicator_results',filters)

    routes={'sources/gaps':'gaps','sources':'registry','mortality/annual':'annual','toxicology/forensic':'forensic','toxicology/assist':'assist','toxicology/treatment':'treatment',
            'naloxone/activity':'naloxone','anomalies/runs':'runs','anomalies/models':'model_metrics',
            'anomalies/sensitivity':'sensitivity','anomalies/diagnostics':'diagnostics','anomalies/zero-baseline':'zero_baseline',
            'evidence/cross-source':'evidence','forecasting/models':'forecast_models','forecasting/results':'forecast','forecasting/backtest':'backtest',
            'forecasting/observations':'forecast_observations','geography/inverclyde':'case_study','geography/comparisons':'rate_comparisons'}
    def handler(resource):
        def endpoint(filters:Annotated[Filters,Query()]):return app.state.service.query(resource,filters)
        return endpoint
    for path,resource in routes.items():app.add_api_route('/api/v1/'+path,handler(resource),methods=['GET'],response_model=Envelope,name=resource)

    @app.get('/api/v1/anomalies',response_model=Envelope)
    def anomalies(filters:Annotated[Filters,Query()]):
        resource='enhanced' if filters.model and filters.model!='phase5_robust' else 'anomalies'
        return app.state.service.query(resource,filters if resource=='enhanced' else filters.model_copy(update={'model':None}))

    @app.get('/api/v1/methodology',response_model=Envelope)
    def methodology():
        rows=app.state.service.artifacts.load('gaps')[0]
        return Envelope(state='ready',kind='metadata',data=[dict(research_prototype=True,foi='Pending; missing alerts never mean no official alert',
             methods=['Prior-only robust median/MAD count screen','Conditional Gamma–Poisson, NB2 moments, seasonal and trend comparators','Historical-origin naive forecasting','NRS registered annual counts and published five-year age-standardised rates'],
             limitations=['No PHS endorsement or operational validation','No Greenock outcomes inferred','Count detections are not prevalence; naloxone is not confirmed overdose incidence','Frozen vintages are not current conditions'],gaps=rows)],total=1)

    @app.get('/api/v1/validation/status',response_model=Envelope)
    def validation():return Envelope(state='ready',kind='metadata',data=[dict(foi_status='pending',external_alert_metrics='unavailable',prospective_validation=False,internal_robustness='Parameter/model sensitivity only; not external event validation',official_alerts='Not populated or inferred from missing records',operational_warning_service=False)],total=1)

    @app.get('/api/v1/reports',response_model=Envelope)
    def reports():return Envelope(state='ready',kind='metadata',data=[dict(title=name,resource=resource) for name,resource in [('Geographic case study','case_study'),('Count-model comparison','model_metrics'),('Source quality gaps','gaps'),('Historical forecast','forecast')]],total=4)

    @app.get('/api/v1/exports')
    def exports(resource:Literal['annual','comparisons','rates','rate_comparisons','anomalies','enhanced','diagnostics','zero_baseline','backtest','forecast_observations','sensitivity','runs','model_metrics','evidence','forecast','forecast_models','mortality_trends','forensic','assist','treatment','naloxone','gaps'],
                request:Request,format:Literal['json','csv']='json'):
        try:
            filters=Filters.model_validate({k:v for k,v in request.query_params.items() if k not in ('resource','format')})
        except ValueError:
            raise QueryError('Invalid export filters') from None
        result=app.state.service.query(resource,filters)
        headers={'Content-Disposition':f'attachment; filename="{resource}.{format}"'}
        if format=='json':return JSONResponse(result.model_dump(mode='json'),headers=headers)
        items=[dict(r,_analytical_version=result.metadata.get('analytical_version'),_artifact_sha256=result.metadata.get('artifact_sha256'),
                    _source=result.metadata.get('source_path'),_limitations='; '.join(result.metadata.get('limitations',[]))) for r in result.data]
        stream=io.StringIO();fields=list(dict.fromkeys(k for row in items for k in row)) or ['_limitations']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in items:
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v for k,v in row.items()})
        return Response(stream.getvalue(),media_type='text/csv',headers=headers)
    return app


app=create_app()
