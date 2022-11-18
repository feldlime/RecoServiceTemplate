from typing import Any, Dict, List, Optional, Sequence

from fastapi import APIRouter, FastAPI, Request, Path
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.log import app_logger
from service.api.RecModels import all_models


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class ErrorObject(BaseModel):
    error_key: str
    error_message: str
    error_loc: Optional[Sequence[str]]


class ErrorResponse(BaseModel):
    errors: List[ErrorObject]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
    response_model=str
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={404: {'model': ErrorResponse}}
)
async def get_reco(
        request: Request,
        model_name: str = Path(..., description='The name of testing model'),
        user_id: int = Path(..., description='The specific id of user'),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in all_models:
        raise ModelNotFoundError(error_message=f'There is no model with name {model_name}')

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    model = all_models[model_name]()
    model.preparing()
    reco = model.get_answer(user_id=user_id,
                            k_recs=k_recs)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
