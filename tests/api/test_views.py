from http import HTTPStatus

import yaml
from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"
with open('./service/envs/authentication_env.yaml') as env_config:
    ENV_TOKEN = yaml.safe_load(env_config)


def test_health(
    client: TestClient,
) -> None:
    with client:
        client.headers = {"Authorization": f"Bearer {ENV_TOKEN['token']}"}
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="model_0", user_id=user_id)
    with client:
        client.headers = {"Authorization": f"Bearer {ENV_TOKEN['token']}"}
        response = client.get(path)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10 ** 10
    path = GET_RECO_PATH.format(model_name="model_0", user_id=user_id)
    with client:
        client.headers = {"Authorization": f"Bearer {ENV_TOKEN['token']}"}
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    model_name = 'unknown_model'
    path = GET_RECO_PATH.format(model_name=model_name, user_id=10 ** 9)
    with client:
        client.headers = {"Authorization": f"Bearer {ENV_TOKEN['token']}"}
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_with_correct_token(
    client: TestClient,
) -> None:
    model_name = 'model_0'
    user_id = 666
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    with client:
        client.headers = {"Authorization": f"Bearer {ENV_TOKEN['token']}"}
        response = client.get(path)
    assert response.status_code == 200


def test_get_reco_with_incorrect_token(
    client: TestClient,
) -> None:
    model_name = 'model_0'
    user_id = 666
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == 401
    assert response.json()["errors"][0]["error_key"] == "token_is_not_correct"
