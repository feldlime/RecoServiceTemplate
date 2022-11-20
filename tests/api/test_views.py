from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


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
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": "Bearer Team_5"})
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(path, headers={"Authorization": "Bearer Team_5"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 123
    incorrect_model = "_"
    path = GET_RECO_PATH.format(model_name=incorrect_model, user_id=user_id)
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(
            path, headers={"Authorization": f"Bearer {incorect_bearer}"}
        )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_bearer_failed(
    client: TestClient,
) -> None:
    user_id = 123
    incorrect_bearer = "lasdkladsk"
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(
            path, headers={"Authorization": f"Bearer {incorrect_bearer}"}
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "incorrect_bearer_key"
