from typing import List
import yaml

from fastapi import APIRouter, FastAPI, Request, Depends
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from service.api.exceptions import (
    UserNotFoundError,
    NotAuthorizedError,
    ModelNotFoundError,
)
from service.api.responses import responses
from service.log import app_logger

with open('config/config.yaml') as stream:
    config = yaml.safe_load(stream)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
bearer_scheme = HTTPBearer()


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
    responses=responses,
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if token.credentials != config['Service']['token']:
        raise NotAuthorizedError(error_message=f"Token {user_id} is incorrect")

    elif model_name not in config['Service']['models']:
        raise ModelNotFoundError(error_message=f"Model name {model_name} not found")

    elif user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    if model_name == 'test_model':
        reco = list(range(k_recs))

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
