from fastapi import APIRouter, Depends, FastAPI, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery

from service.api.exceptions import (
    CredentialError,
    ModelNotFoundError,
    UserNotFoundError,
)
from service.log import app_logger

from .config import config_env
from .models import NotFoundError, RecoResponse, UnauthorizedError
from .models_zoo import DumpModel, OnlineModel

import sentry_sdk

router = APIRouter()

api_query = APIKeyQuery(name=config_env["API_KEY_NAME"], auto_error=False)
api_header = APIKeyHeader(name=config_env["API_KEY_NAME"], auto_error=False)
token_bearer = HTTPBearer(auto_error=False)

sentry_sdk.init(
    dsn="https://687935e2f3184212a6eeea6eb4784c7d@o4504984015798272.ingest"
        + ".sentry.io/4504984017305600",
    traces_sample_rate=1.0,
)

try:
    models_zoo = {
        "model_1": DumpModel(),
        "LightFM": OnlineModel(path_to_model='./data/lightfm.pickle')
    }
except FileNotFoundError:
    models_zoo = {
        "model_1": DumpModel(),
    }


async def get_api_key(
    api_key_query: str = Security(api_query),
    api_key_header: str = Security(api_header),
    token: HTTPAuthorizationCredentials = Security(token_bearer),
):
    if api_key_query == config_env["API_KEY"]:
        return api_key_query
    if api_key_header == config_env["API_KEY"]:
        return api_key_header
    if token is not None and token.credentials == config_env["API_KEY"]:
        return token.credentials
    sentry_sdk.capture_exception(error=Exception('Token Error'))
    raise CredentialError()


@router.get(path="/health", tags=["Health"])
async def health(api_key: APIKey = Depends(get_api_key)) -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={
        404: {"model": NotFoundError, "user": NotFoundError},
        401: {"model": UnauthorizedError},
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    api_key: APIKey = Depends(get_api_key),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10 ** 7:
        sentry_sdk.capture_exception(
            error=Exception(f"User {user_id} not found"))
        raise UserNotFoundError(
            error_message=Exception(f"User {user_id} not found"))

    if user_id % 666 == 0:
        sentry_sdk.capture_exception(
            error=Exception(f"User id {user_id} is divided entirely into 666"))
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in models_zoo.keys():
        sentry_sdk.capture_exception(
            error=Exception(f"Model {model_name} not found"))
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    k_recs = request.app.state.k_recs

    reco = models_zoo[model_name].reco_predict(
        user_id=user_id,
        k_recs=k_recs
    )

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
