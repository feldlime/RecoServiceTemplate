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
        response = client.get(path)
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
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unauthorized_user(
    client: TestClient,
) -> None:
    user_id = 777
    wrong_bearer = "12345qwerty"
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(
            path, headers={"Authorization": f"Bearer {wrong_bearer}"}
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "unauthorized_request"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 777
    wrong_model_name = "unknown_model"
    path = GET_RECO_PATH.format(model_name=wrong_model_name, user_id=user_id)
    with client:
        response = client.get(
            path, headers={"Authorization": f"Bearer YUNHUSLUSUFCOHUY"}
        )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"

