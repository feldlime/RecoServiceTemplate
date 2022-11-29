from typing import List

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.log import app_logger
from service.models import Error

model_name_list = ["model_1"]

class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


not_found_examples = {
    "user not found": {
        "value": [
            {
                "error_key": "user_not_found",
                "error_message": "user not found",
                "error_loc": None,
            },
        ],
    },
    "model not found": {
        "value": [
            {
                "error_key": "model_not_found",
                "error_message": "model not found",
                "error_loc": None,
            },
        ],
    },
}

recommendations_example = {
  "user_id": 0,
  "items": list(range(10)),
}


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
            "model": List[Error],
            "content": {
                "application/json": {
                    "examples": not_found_examples,
                },
            },
        },
    },
)

async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in model_name_list:
        raise ModelNotFoundError(error_message=f"{model_name} not found")
    
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")



    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
