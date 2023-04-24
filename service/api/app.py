import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict

import sentry_sdk
import uvloop
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from ..log import app_logger, setup_logging
from ..settings import ServiceConfig
from .exception_handlers import add_exception_handlers
from .middlewares import add_middlewares
from .views import add_views

__all__ = ("create_app",)

sentry_sdk.init(
    dsn="https://0b78febaac224b32b28674413c94a0b0@o4505051663630336.ingest.sentry.io/4505051666251776",
    traces_sample_rate=1.0,
)

def setup_asyncio(thread_name_prefix: str) -> None:
    uvloop.install()

    loop = asyncio.get_event_loop()

    executor = ThreadPoolExecutor(thread_name_prefix=thread_name_prefix)
    loop.set_default_executor(executor)

    def handler(_, context: Dict[str, Any]) -> None:
        message = "Caught asyncio exception: {message}".format_map(context)
        app_logger.warning(message)

    loop.set_exception_handler(handler)


def create_app(config: ServiceConfig) -> FastAPI:
    setup_logging(config)
    setup_asyncio(thread_name_prefix=config.service_name)

    app = FastAPI(debug=False)
    app.state.k_recs = config.k_recs
    app.state.token = config.token
    app.state.models = config.models

    Instrumentator().instrument(app).expose(app)

    add_views(app)
    add_middlewares(app)
    add_exception_handlers(app)

    return app
