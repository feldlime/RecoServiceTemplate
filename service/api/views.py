from typing import List

import yaml
from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError, NotAuthorizedError, \
    ModelNotFoundError
from service.log import app_logger

config_file = "config/config.yaml"
with open(config_file) as f:
    config = yaml.load(f, Loader=yaml.Loader)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()

auth = HTTPBearer()


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
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth)
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here

    if token.credentials != config['auth']['token']:
        raise NotAuthorizedError(error_message=f"Token: {token} not found",
                                 status_code=401)

    if model_name not in config['service']['models']:
        raise ModelNotFoundError(error_message=f"Model: "
                                               f"{model_name} not found")

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    k_recs = request.app.state.k_recs
    if model_name == "test_model":
        reco = list(range(k_recs))
        return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
