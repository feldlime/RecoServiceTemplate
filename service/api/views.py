from typing import List
from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel
import dill
from service.api.exceptions import ModelNotFoundError, UnauthorizedUserError, UserNotFoundError
from service.log import app_logger
import pandas as pd
from service.models import recommend_popular


# load predictions of dssm model
dssm_preds = pd.read_csv("dssm_predictions.csv") 
dssm_preds.item_id = dssm_preds.item_id.apply(lambda x: [int(i) for i in x[1:-1].split(", ")])


# get popular recommendations
interactions = pd.read_csv('data/interactions.csv')
interactions['last_watch_dt'] = pd.to_datetime(interactions['last_watch_dt'])
interactions.rename(
    columns={
        'last_watch_dt': 'datetime',
        'total_dur': 'weight',
            },
    inplace=True,
    )
popular_recs = recommend_popular(interactions)
popular_recs_30 = recommend_popular(interactions, days = 30)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]

router = APIRouter()

@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"



@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse
)
async def get_reco(
    request: Request, 
    model_name: str, 
    user_id: int, 
    # token=Depends(bearer)
    ) -> RecoResponse:
    # app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")
    app_logger.info(f"Request for model: {model_name}")
    app_logger.info(f"Request for user: {user_id}")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    
    if model_name == "DSSM":
        try:
            recs_list = dssm_preds[dssm_preds.user_id == user_id].item_id.values[0]
        except:
            recs_list = popular_recs_30

    return RecoResponse(user_id=user_id, items=recs_list)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
