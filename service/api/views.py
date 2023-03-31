from typing import List

import yaml
from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel

from models.load_models import ALS, ANN, LIGHTFM, POPULAR, SVD, USERKNN
from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.auth.authorization import JWTBearer
from service.log import app_logger


with open('config/config_service.yml') as stream:
    config_service = yaml.safe_load(stream)['config']
with open('config/config_models.yml') as stream:
    config_model = yaml.safe_load(stream)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class Message(BaseModel):
    message: str


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
    dependencies=[Depends(JWTBearer())]
)
async def health() -> str:
    return "I am alive - 36.6"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    dependencies=[Depends(JWTBearer())],
    responses={
        200: {"response": RecoResponse},
        403: {"response": Message},
        404: {"response": Message},
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in config_service['models']:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if model_name == 'userknn_model':
        # Online
        if config_model['UserKnn_model_conf']['online']:
            print("Online")
            model = USERKNN['model']
            reco = model.predict_online(
                user_id,
                config_model['UserKnn_model_conf']['N_recs'],
            )
        # Ofline
        else:
            userknn_reco_df = USERKNN['reco_df']
            reco = userknn_reco_df[userknn_reco_df.user_id == user_id]
        popular_reco_df = POPULAR['reco_df']
        reco_popular = list(popular_reco_df.item_id)
        i = 0
        if len(reco) == config_model['UserKnn_model_conf']['N_recs']:
            threshold = config_model['UserKnn_model_conf']['blend_threshold']
            reco = reco[reco.score > threshold]

        reco = list(reco.item_id)
        while len(reco) < config_model['UserKnn_model_conf']['N_recs']:
            if reco_popular[i] not in reco:
                reco.append(reco_popular[i])
            i += 1
    elif model_name == 'popular_model':
        popular_reco_df = POPULAR['reco_df']
        reco = list(popular_reco_df.item_id)
    elif model_name == 'als_model':
        als_reco_df = ALS['reco_df']
        popular_reco_df = POPULAR['reco_df']
        if user_id in als_reco_df.user_id.unique():
            reco = list(als_reco_df[als_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'svd_model':
        svd_reco_df = SVD['reco_df']
        popular_reco_df = POPULAR['reco_df']
        if user_id in svd_reco_df.user_id.unique():
            reco = list(svd_reco_df[svd_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'lightfm_model':
        lightfm_reco_df = LIGHTFM['reco_df']
        popular_reco_df = POPULAR['reco_df']
        if user_id in lightfm_reco_df.user_id.unique():
            reco = list(
                lightfm_reco_df[lightfm_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'ann_model':
        model = ANN['model']
        popular_reco_df = POPULAR['reco_df']
        if user_id < len(model.label):
            reco = list(model.predict(user_id))
        else:
            reco = list(popular_reco_df.item_id)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
