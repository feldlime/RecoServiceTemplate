from http import HTTPStatus

from starlette.testclient import TestClient


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
