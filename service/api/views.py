from typing import List
import yaml

from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel

from models.load_models import Popular, UserKNN, ALS, SVD, LightFM, ANN
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
    dependencies=[Depends(JWTBearer())],
)
async def health() -> str:
    return "36.6"


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

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in config_service['models']:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if model_name == 'test_model':
        k_recs = request.app.state.k_recs
        reco = list(range(k_recs))
    elif model_name == 'userknn_model':
        userknn_reco_df = UserKNN['reco_df']
        popular_reco_df = Popular['reco_df']
        if user_id in userknn_reco_df.user_id.unique():
            reco = list(userknn_reco_df[userknn_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'popular_model':
        popular_reco_df = Popular['reco_df']
        reco = list(popular_reco_df.item_id)
    elif model_name == 'als_model':
        als_reco_df = ALS['reco_df']
        popular_reco_df = Popular['reco_df']
        if user_id in als_reco_df.user_id.unique():
            reco = list(als_reco_df[als_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'svd_model':
        svd_reco_df = SVD['reco_df']
        popular_reco_df = Popular['reco_df']
        if user_id in svd_reco_df.user_id.unique():
            reco = list(svd_reco_df[svd_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'lightfm_model':
        lightfm_reco_df = LightFM['reco_df']
        popular_reco_df = Popular['reco_df']
        if user_id in lightfm_reco_df.user_id.unique():
            reco = list(lightfm_reco_df[lightfm_reco_df.user_id == user_id].item_id)
        else:
            reco = list(popular_reco_df.item_id)
    elif model_name == 'ann_model':
        model = ANN['model']
        popular_reco_df = Popular['reco_df']
        if user_id < len(model.label):
            reco = list(model.predict(user_id))
        else:
            reco = list(popular_reco_df.item_id)

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
