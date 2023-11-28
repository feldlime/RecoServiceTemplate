import os
import pickle
import random
from http import HTTPStatus
from typing import List

import pandas as pd
from fastapi import APIRouter, FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError
from service.log import app_logger


class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'UserKnn':
            from service.userknn import UserKnn
            return UserKnn
        return super().find_class(module, name)


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    with open(path, 'rb') as f:
        try:
            return CustomUnpickler(f).load()
        except Exception as e:
            raise RuntimeError(f"Failed to load the model from '{path}': {e}")


MODEL_PATH = "service/models/baseknn.pkl"

try:
    userknn = load_model(MODEL_PATH)
except Exception as e:
    print(f"An error occurred: {e}")


class NotFoundModel(BaseModel):
    detail: str


class UnauthorizedModel(BaseModel):
    detail: str


class InternalServerErrorModel(BaseModel):
    detail: str


security = HTTPBearer()
API_KEY = "i_love_recsys"
VALID_MODELS = ['some_model', 'best_random', 'knn']


async def verify_token(
    http_authorization_credentials: HTTPAuthorizationCredentials = Security(
        security)):
    token = http_authorization_credentials.credentials
    if token != API_KEY:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Invalid or missing token")


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
    responses={
        200: {
            "description": "Successful health response",
        },
        500: {
            "description": "Internal server error",
            "model": InternalServerErrorModel,
        }
    }
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    dependencies=[Security(verify_token)],
    responses={
        200: {
            "description": "Successful response with recommendations",
            "model": RecoResponse,
        },
        404: {
            "description": "Model not found or user not found",
            "model": NotFoundModel,
        },
        401: {
            "description": "Unauthorized access",
            "model": UnauthorizedModel,
        },
        500: {
            "description": "Internal server error",
            "model": InternalServerErrorModel,
        }
    }
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Запрос на модель: {model_name}, user_id: {user_id}")
    reco = process_reco_request(request, model_name, user_id)
    return RecoResponse(user_id=user_id, items=reco)


def process_reco_request(request: Request, model_name: str, user_id: int) -> \
List[int]:
    if model_name not in VALID_MODELS and model_name != "best_random":
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"Модель {model_name} не найдена")

    if user_id > 10 ** 9:
        raise UserNotFoundError(
            error_message=f"Пользователь {user_id} не найден")

    if model_name == "best_random":
        reco = random.sample(range(0, 10), 10)
    elif model_name == 'knn':
        reco = userknn.predict(
            pd.DataFrame([user_id], columns=['user_id']),
            N_recs=10).item_id.to_list()
    else:
        k_recs = request.app.state.k_recs
        reco = list(range(k_recs))

    return reco


def add_views(app: FastAPI) -> None:
    app.include_router(router)
