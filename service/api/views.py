import os
from typing import List

from fastapi import APIRouter, Depends, FastAPI, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery
from pydantic import BaseModel

from service.api.exceptions import (
    AuthorizationError,
    ModelNotFoundError,
    UserNotFoundError,
)
from service.log import app_logger
from service.recmodels.config import init_config


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
models = init_config()


ACCESS_KEY = os.getenv("ACCESS_KEY", "")

access_key_query = APIKeyQuery(name="access_key", auto_error=False)
access_key_header = APIKeyHeader(name="access_key", auto_error=False)
token_bearer = HTTPBearer(auto_error=False)


async def get_access_key(
    access_key_from_query: str = Security(access_key_query),
    access_key_from_header: str = Security(access_key_header),
    token: HTTPAuthorizationCredentials = Security(token_bearer),
) -> str:
    if access_key_from_header == ACCESS_KEY:
        return access_key_from_header
    elif access_key_from_query == ACCESS_KEY:
        return access_key_from_query
    elif token is not None and token.credentials == ACCESS_KEY:
        return token.credentials
    else:
        raise AuthorizationError(error_message="Token is invalid")


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
    responses={
        404: {"description": "User or model are not found"},
        401: {"description": "Authorization failed"},
    },
)

async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    access_key: APIKey = Depends(get_access_key),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in models.keys():
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    reco = models[model_name].get_items_reco(user_id, k_recs)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
