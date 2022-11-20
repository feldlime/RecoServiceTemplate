import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict

import uvloop
from fastapi import FastAPI

from ..log import app_logger, setup_logging
from ..settings import ServiceConfig
from .exception_handlers import add_exception_handlers
from .middlewares import add_middlewares
from .views import add_views

__all__ = ("create_app",)


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

    app = FastAPI(
        debug=False,
        title="RecoService API",
        version="1.0.0",
        description="""API for recommendations using different models provided by
                    **ITMO RecSys team 4** based on OpenAPI-3.0.2.
                    You can use our RecoService API if you wish to build and
                    maintain your own UI or integrate it into an existing
                    framework.""",
        termsOfService="http://itmo-mts-team-4.com/terms/",
        contact={
            "name": "ITMO RecSys team 4",
            "url": "http://www.itmo-mts-team-4.com/support",
            "email": "support@itmo-mts-team-4.com",
        },
        license={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        servers=[
            {"url": "http://localhost:8080", "description": "Local Development Server"},
            {
                "url": "https://gamma-examination-sir-sa.trycloudflare.com",
                "description": "Testing Server",
            },
            {
                "url": "https://stoplight.io/mocks/iloncka/recoservice-1-0-0/84330",
                "description": "Mock Server",
            },
        ],
    )
    app.state.k_recs = config.k_recs

    add_views(app)
    add_middlewares(app)
    add_exception_handlers(app)

    return app
