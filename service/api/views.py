from http import HTTPStatus
from typing import List

from fastapi import APIRouter, FastAPI
from fastapi.param_functions import Query
from pydantic import BaseModel
from starlette.responses import JSONResponse

from service.log import app_logger
from service.response import create_response


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class ManyRecoResponse(BaseModel):
    data: List[RecoResponse]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def ping() -> JSONResponse:
    return create_response(message="I am alive :)", status_code=HTTPStatus.OK)


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Health"],
    response_model=ManyRecoResponse,
)
async def get_reco(model_name: str, user_id: str, n: int = Query(10_000)) -> ManyRecoResponse:
    # Write your code
    app_logger.info(f"Request for user_id: {user_id}")

    if model_name == "model_1":
        reco = list(range(10))
    elif model_name == "model_2":
        reco = [9906, 14534,  5874, 11574, 14, 7098, 9242, 15422,  2582, 5701]
    else:
        raise ValueError

    responses = [RecoResponse(user_id=user_id, items=reco)] * n
    return ManyRecoResponse(data=responses)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
