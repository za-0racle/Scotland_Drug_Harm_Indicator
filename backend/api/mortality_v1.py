"""Separate versioned GET route; legacy routes and consumers are unchanged."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Request
from backend.schemas.mortality_v1 import MortalityPage
from backend.services.mortality_adapter import MortalityAdapter, CollectionConflict

router = APIRouter()


@router.get('/api/v1/analytical/v1/mortality-trends', response_model=MortalityPage, tags=['Analytical contract v1'])
def mortality_trends_v1(request: Request,
                       offset: Annotated[int, Query(ge=0, le=1000000)] = 0,
                       limit: Annotated[int, Query(ge=1, le=1000)] = 100,
                       expected_collection: Annotated[str | None, Query(pattern=r'^[0-9a-f]{64}$')] = None):
    if set(request.query_params) - {'offset', 'limit', 'expected_collection'}:
        raise HTTPException(422, 'Unsupported analytical query parameter')
    try:
        return MortalityAdapter(request.app.state.service.artifacts).page(offset, limit, expected_collection)
    except CollectionConflict as error:
        raise HTTPException(409, str(error)) from None
    except ValueError:
        raise HTTPException(422, 'Invalid analytical pagination') from None
