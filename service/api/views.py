from typing import List

from fastapi import APIRouter, FastAPI, Request,HTTPException
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError, ModelNotFoundError
from service.log import app_logger
import pandas as pd
import pickle

with open("user_knn_model.pkl", "rb") as file:
    user_knn_model = pickle.load(file)

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

    if model_name not in ["personal", "anotherModel"]:  # Add your model names
        raise HTTPException(status_code=404, detail="Model not found")
    
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    # Generate recommendations using your UserKnn model
    reco_df = user_knn_model.predict(pd.DataFrame({'user_id': [user_id]}))
    reco_items = reco_df['item_id'].tolist()

    return RecoResponse(user_id=user_id, items=reco_items)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
