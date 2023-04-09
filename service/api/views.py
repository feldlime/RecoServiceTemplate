from typing import List

import yaml
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import (
    ModelNotFoundError,
    NotAuthorizedError,
    UserNotFoundError,
)
from service.api.responses import responses
from service.log import app_logger
from service.reco_models.model_classes import Popular, UserKNN, LightFM

# config_file = 'service/config/config.yaml'
with open('service/config/config.yaml') as stream:
    config = yaml.safe_load(stream)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
bearer_scheme = HTTPBearer()

UserKNN.load_model()
Popular.load_model()
LightFM.load_model()


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
    global reco
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # errors
    if token.credentials != request.app.state.token:
        raise NotAuthorizedError(error_message=f"Token {user_id} is incorrect")
    elif model_name not in request.app.state.models:
        raise ModelNotFoundError(
            error_message=f"Model name {model_name} not found"
        )
    elif user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    # models
    k_recs = request.app.state.k_recs
    if model_name == 'test_model':
        reco = list(range(config['test_model']['n_recs']))

    elif model_name == 'userknn_model':
        # Online
        if config['userknn_model']['online_mode']:
            userknn_model = UserKNN.model
            reco = userknn_model.predict(user_id, k_recs)

            if not reco:
                reco = list(Popular.recs.item_id)

        # Offline
        else:
            userknn_reco = UserKNN.recs
            reco = userknn_reco[userknn_reco.user_id == user_id]
            if len(reco) == 0:
                reco = []
            elif len(reco) <= k_recs:
                reco = reco[reco.score > 1.5]
                reco = list(reco.item_id)

            popular_recs = Popular.recs
            popular_reco = list(popular_recs.item_id)
            i = 0
            while len(reco) < k_recs:
                if popular_reco[i] not in reco:
                    reco.append(popular_reco[i])
                i += 1

    elif model_name == 'lightfm_model':
        # Online
        lightfm_model = LightFM.model
        reco = lightfm_model.recommend(user_id, k_recs)

        if not reco:
            reco = list(Popular.recs.item_id)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
