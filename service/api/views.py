from typing import List

import yaml
from fastapi import APIRouter, Depends, FastAPI, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import (
    AuthenticateError,
    ModelNotFoundError,
    UserNotFoundError,
)
from service.config.responses_cfg import example_responses
from service.log import app_logger

with open('./service/config/models.yaml') as models_config:
    MODEL_PARAMS = yaml.safe_load(models_config)

with open('./service/envs/authentication_env.yaml') as env_config:
    ENV_TOKEN = yaml.safe_load(env_config)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
auth_scheme = HTTPBearer(auto_error=False)


async def authorization_by_token(
    token: HTTPAuthorizationCredentials = Security(auth_scheme),
):
    if token is not None and token.credentials == ENV_TOKEN['token']:
        return token.credentials
    else:
        raise AuthenticateError()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health(
    token: HTTPAuthorizationCredentials = Depends(authorization_by_token)
) -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses=example_responses,
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(authorization_by_token),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in MODEL_PARAMS['models']:
        raise ModelNotFoundError(
            error_message=f"Model name '{model_name}' not found"
        )

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
