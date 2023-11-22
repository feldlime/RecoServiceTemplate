# pylint: disable=redefined-outer-name
import random
import string

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from service.api.app import create_app
from service.settings import ServiceConfig, get_config


@pytest.fixture
def service_config() -> ServiceConfig:
    return get_config()


@pytest.fixture
def app(
    service_config: ServiceConfig,
) -> FastAPI:
    app = create_app(service_config)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def unknown_model() -> str:
    return "".join(random.choices(string.ascii_letters))
