from http import HTTPStatus

from dotenv import dotenv_values
from starlette.testclient import TestClient

from service.settings import ServiceConfig

config = dotenv_values()

GET_RECO_PATH = "/reco/{model_name}/{user_id}"
CORRECT_AUTH = f"Bearer {config['TOKEN']}"
CORRECT_MODEL_NAME = "dummy_model"


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name=CORRECT_MODEL_NAME, user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": CORRECT_AUTH})
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name=CORRECT_MODEL_NAME, user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": CORRECT_AUTH})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="wrong_model_name", user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": CORRECT_AUTH})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_for_wrong_auth(
    client: TestClient,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name=CORRECT_MODEL_NAME, user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": "Bearer wrong_token"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "wrong_token"


def test_get_reco_for_no_auth(
    client: TestClient,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name=CORRECT_MODEL_NAME, user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["errors"][0]["error_key"] == "http_exception"
