from typing import List

import pandas as pd
import yaml
from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from service.config.responses import responses

from service.api.exceptions import UserNotFoundError, NotAuthorizedError, \
    ModelNotFoundError
from service.log import app_logger
from userknn import UserKnn

config_file = "config/config.yaml"
with open(config_file) as f:
    config = yaml.load(f, Loader=yaml.Loader)

userknn_recos_off = pd.read_csv('service/pretrained_models/my_datas.csv')

popular_model_recs = [15297, 10440, 4151, 13865, 9728, 3734, 12192, 142, 2657, 4880]

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
    responses=responses
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

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name == "userknn_model":
        k_recs = request.app.state.k_recs
        reco = eval(userknn_recos_off.loc[user_id, "item_id"])

    elif model_name == "test_model":
        k_recs = request.app.state.k_recs
        reco = list(range(k_recs))

    elif model_name == "popular_model":
        k_recs = request.app.state.k_recs
        reco = popular_model_recs

    else:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
