import os
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery
from pydantic import BaseModel

from service.api.exceptions import (
    ModelNotFoundError,
    NotAuthorizedError,
    UserNotFoundError,
)
from service.log import app_logger

load_dotenv()


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


api_key_query = APIKeyQuery(name='API_KEY', auto_error=False)
api_key_header = APIKeyHeader(name='API_KEY', auto_error=False)
token_bearer = HTTPBearer(auto_error=False)

API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise Exception(
        "API_KEY is not set. "
        "You can set it in .env file or in the environment variables.")


async def get_api_key(
    api_key_from_query: str = Security(api_key_query),
    api_key_from_header: str = Security(api_key_header),
    token: HTTPAuthorizationCredentials = Security(token_bearer),
):
    if api_key_from_query == API_KEY:
        return api_key_from_query
    if api_key_from_header == API_KEY:
        return api_key_from_header
    if token is not None and token.credentials == API_KEY:
        return token.credentials
    raise NotAuthorizedError()


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
    responses={404: {"description": "User or model not found"},
               401: {"description": "Not authorized"}},
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    api_key: APIKey = Depends(get_api_key)
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name == 'dummy_model':
        k_recs = request.app.state.k_recs
    else:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
