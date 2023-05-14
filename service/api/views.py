from typing import List

import yaml
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import (
    Error666,
    ModelNotFoundError,
    NotAuthorizedError,
    UserNotFoundError,
)
from service.api.responses import responses
from service.log import app_logger
from service.reco_models.model_classes import Popular, UserKNN, PopularByAge

# config_file = 'service/config/config.yaml'
with open('service/config/config.yaml') as stream:
    config = yaml.safe_load(stream)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class ExplainResponse(BaseModel):
    p: int
    explanation: str


router = APIRouter()
bearer_scheme = HTTPBearer()

UserKNN.load_model()
Popular.load_model()
# LightFM.load_model()
PopularByAge.load_model()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


async def check_errors(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if token.credentials != request.app.state.token:
        raise NotAuthorizedError(error_message=f"Token {user_id} is incorrect")
    elif model_name not in request.app.state.models:
        raise ModelNotFoundError(
            error_message=f"Model name {model_name} not found"
        )
    elif user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    elif user_id % 666 == 0:
        raise Error666(error_message=f"User {user_id} is wrong")


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses=responses,
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> RecoResponse:
    global reco
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    await check_errors(request, model_name, user_id, token)

    # models
    k_recs = request.app.state.k_recs
    if model_name == 'test_model':
        reco = list(range(k_recs))

    elif model_name == 'userknn_model':
        # Online
        if config['userknn_model']['online_mode']:
            userknn_model = UserKNN.model
            reco = userknn_model.predict(user_id, k_recs)

            if not reco:
                reco = list(Popular.recs.item_id)

        # Offline
        else:
            userknn_reco = UserKNN.recs
            reco = userknn_reco[userknn_reco.user_id == user_id]
            if len(reco) == 0:
                reco = []
            elif len(reco) <= k_recs:
                reco = reco[reco.score > 1.5]
                reco = list(reco.item_id)

            popular_recs = Popular.recs
            popular_reco = list(popular_recs.item_id)
            i = 0
            while len(reco) < k_recs:
                if popular_reco[i] not in reco:
                    reco.append(popular_reco[i])
                i += 1

    # elif model_name == 'lightfm_model':
    #     # Online
    #     lightfm_model = LightFM.model
    #     reco = lightfm_model.recommend(user_id, k_recs)
    #
    #     if not reco:
    #         reco = list(Popular.recs.item_id)
    return RecoResponse(user_id=user_id, items=reco)


@router.get(
    path="/explain/{model_name}/{user_id}/{item_id}",
    tags=["Explanations"],
    response_model=ExplainResponse,
)
async def explain(
    request: Request,
    model_name: str,
    user_id: int,
    item_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> ExplainResponse:
    """
    Пользователь переходит на карточку контента, на которой нужно показать
    процент релевантности этого контента зашедшему пользователю,
    а также текстовое объяснение почему ему может понравиться этот контент.

    :param request: запрос.
    :param model_name: название модели, для которой нужно получить объяснения.
    :param user_id: id пользователя, для которого нужны объяснения.
    :param item_id: id контента, для которого нужны объяснения.
    :param token: токен для аутентификации
    :return: Response со значением процента релевантности и текстовым
             объяснением, понятным пользователю.
    - "p": "процент релевантности контента item_id для пользователя user_id"
    - "explanation": "текстовое объяснение почему рекомендован item_id"
    """
    global reco
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    await check_errors(request, model_name, user_id, item_id, token)
    p = 1
    exp = 'abc'
    return ExplainResponse(p=p, explanation=exp)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
