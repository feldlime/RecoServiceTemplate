from typing import List, Optional, Sequence

import numpy as np
from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.api.models import MODELS
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class NotFoundError(BaseModel):
    error_key: str
    error_message: str
    error_loc: Optional[Sequence[str]]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={404: {"model": NotFoundError}, 200: {"model": RecoResponse}},
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in MODELS:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    # Write your code here

    k_recs = request.app.state.k_recs

    if model_name == "random":
        # Just a random generation of recomendations
        np.random.seed(user_id)
        reco = np.random.randint(10, 1000, size=k_recs).tolist()

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
