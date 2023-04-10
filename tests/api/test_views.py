from http import HTTPStatus

from starlette.testclient import TestClient

from service.api.config import config_env
from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"
HEADER = {config_env['API_KEY_NAME']: config_env["API_KEY"]}


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health", headers=HEADER)
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="model_1", user_id=user_id)
    with client:
        response = client.get(path, headers=HEADER)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10 ** 10
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    with client:
        response = client.get(path, headers=HEADER)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 1
    model_name = 'model_2'
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    with client:
        response = client.get(path, headers=HEADER)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_with_wrong_cred(
    client: TestClient,
) -> None:
    user_id = 123
    model_name = 'model_1'
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    wrong_header = {config_env['API_KEY_NAME']: "random_key"}
    with client:
        response = client.get(path, headers=wrong_header)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["errors"][0]["error_key"] == "wrong_credentials"
