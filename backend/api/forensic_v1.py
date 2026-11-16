"""Separate versioned read-only route for the Phase 4 forensic resource."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from backend.schemas.forensic_v1 import ForensicPage
from backend.services.forensic_adapter import ForensicAdapter, ForensicCollectionConflict

router = APIRouter()


@router.get('/api/v1/analytical/v1/forensic-toxicology', response_model=ForensicPage, tags=['Analytical contract v1'])
def forensic_toxicology_v1(
    request: Request,
    offset: Annotated[int, Query(ge=0, le=1000000)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    expected_collection: Annotated[str | None, Query(pattern=r'^[0-9a-f]{64}$')] = None,
):
    if set(request.query_params) - {'offset', 'limit', 'expected_collection'}:
        raise HTTPException(422, 'Unsupported analytical query parameter')
    try:
        return ForensicAdapter(request.app.state.service.artifacts).page(offset, limit, expected_collection)
    except ForensicCollectionConflict as error:
        raise HTTPException(409, str(error)) from None
    except ValueError:
        raise HTTPException(422, 'Invalid forensic analytical pagination') from None
