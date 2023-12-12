from typing import List

from fastapi import APIRouter, FastAPI, Request,HTTPException
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError, ModelNotFoundError
from service.log import app_logger
import pandas as pd
from service.api import user_knn,autoencoder,dsmm,recbole

import pickle
from service.api.user_knn import load
import os

user_knn_path = 'service/api/user_knn_model.pkl'
userknn_model = load(user_knn_path)

class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "200"



@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={
        200: {
            "description": "Successful response",
            "model": RecoResponse,
        },
        404: {
            "description": "Model not found or User not found",
            "content": {"application/json": {"example": {"detail": "Model not found"}}},
        },
    },

)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    k_recs = request.app.state.k_recs

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    elif model_name == userknn_model:
        reco_df = userknn_model.recommendation(user_id,N_recs=k_recs)
    elif model_name == autoencoder:
        reco_df = autoencoder.recommend_items(user_id,N_recs=k_recs)
    elif model_name == dsmm:
        reco_df = dsmm.recommend(user_id,N_recs=k_recs)
    elif model_name == recbole:
        reco_df = recbole.recommend_items_to_user(user_id,N_recs=k_recs)
    # Generate recommendations using your UserKnn model
    
    
    
    #user_knn_model = load_user_knn_model("service/api/user_knn_model.pkl")
    #reco_df = request.app.state.k_recs
    #reco_items = pd.DataFrame({'user_id': [123, 456, 789]}) 
    
    
    return RecoResponse(user_id=user_id, items=reco_df)


def add_views(app: FastAPI) -> None:
    app.include_router(router)

