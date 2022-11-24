import os.path
import pickle
from typing import List

from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.auth_bearer import JWTBearer
from service.gdown_utils import download_file_from_google_drive
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
available_models = ["recsys_model"]

model_name = 'model.sav'
dataset_name = 'dataset.sav'
if not os.path.exists(model_name):
    download_file_from_google_drive('1HCALVMCHKVPekBPq8_8HXW6oubM5Kgjv',
                                    model_name)
if not os.path.exists(dataset_name):
    download_file_from_google_drive('1-FOStMxn6Z-VA22xE70aeLa0noWZEfIq',
                                    dataset_name)

model = pickle.load(open(model_name, 'rb'))
dataset = pickle.load(open(dataset_name, 'rb'))


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
    responses={
        404: {
            "description": "Model not found"
        }
    },
    dependencies=[Depends(JWTBearer())]
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in available_models:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    k_recs = request.app.state.k_recs
    recs = model.recommend(
        [user_id],
        dataset=dataset,
        k=k_recs,
        filter_viewed=False
    )['item_id'].values.tolist()
    return RecoResponse(user_id=user_id, items=recs)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
