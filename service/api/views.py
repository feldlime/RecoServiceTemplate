from __future__ import annotations

import random
from typing import Union

from decouple import config
from fastapi import APIRouter, Depends, FastAPI, Request

from service.api.auth.auth_bearer import JWTBearer
from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.log import app_logger

from ..models import ForbiddenError, HealthResponse, HTTPValidationError, NotFoundError, RecoResponse, UnauthorizedError

MODELS = config("models")


router = APIRouter()


@router.get(path="/health", tags=["Health"], response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Check health
    """
    return HealthResponse(health="I am alive. Everything is OK!")


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    dependencies=[Depends(JWTBearer())],
    response_model=RecoResponse,
    responses={
        "200": {"model": RecoResponse},
        "401": {"model": UnauthorizedError},
        "403": {"model": ForbiddenError},
        "404": {"model": NotFoundError},
        "422": {"model": HTTPValidationError},
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> Union[RecoResponse, UnauthorizedError, NotFoundError, HTTPValidationError]:
    """
    Get recommendations for user
    """
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in MODELS:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    # Write your code here

    k_recs = request.app.state.k_recs

    if model_name == "random":
        # Just a random generation of recomendations
        reco = random.sample(range(1000), k_recs)

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
