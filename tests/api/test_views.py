from http import HTTPStatus

from starlette.testclient import TestClient

GET_RECO_PATH = "/reco/{user_id}"


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
) -> None:
    user_id = "123"
    path = GET_RECO_PATH.format(user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"items": ["123a", "123b"]}


def test_get_reco_404(
    client: TestClient,
) -> None:
    user_id = "1234"
    path = GET_RECO_PATH.format(user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"
