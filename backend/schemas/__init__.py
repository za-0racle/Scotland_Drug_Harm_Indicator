from datetime import date
from typing import Any,Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator


class Filters(BaseModel):
    model_config=ConfigDict(extra='forbid')
    geography_id:str|None=Field(None,max_length=100)
    boundary_type:str|None=Field(None,max_length=50)
    indicator:str|None=Field(None,max_length=160)
    category:str|None=Field(None,max_length=160)
    model:str|None=Field(None,max_length=100)
    compare_to:str|None=Field(None,max_length=100)
    start_year:int|None=Field(None,ge=1900,le=2100)
    end_year:int|None=Field(None,ge=1900,le=2100)
    start_date:date|None=None
    end_date:date|None=None
    offset:int=Field(0,ge=0,le=1000000)
    limit:int=Field(100,ge=1,le=1000)
    signals_only:bool=True

    @model_validator(mode='after')
    def order(self):
        if self.start_year and self.end_year and self.start_year>self.end_year:
            raise ValueError('Start year exceeds end year')
        if self.start_date and self.end_date and self.start_date>self.end_date:
            raise ValueError('Start date exceeds end date')
        return self


class Envelope(BaseModel):
    state:Literal['ready','empty','unavailable','error']
    kind:Literal['research_result','database_observation','metadata','unavailable_evidence']
    data:list[dict[str,Any]]=Field(default_factory=list)
    total:int=0
    offset:int=0
    limit:int=100
    metadata:dict[str,Any]=Field(default_factory=dict)
    message:str=''
