from fastapi import FastAPI

from ..log import setup_logging
from ..settings import ServiceConfig
from .exception_handlers import add_exception_handlers
from .middlewares import add_middlewares
from .views import add_views

__all__ = ("create_app",)


def create_app(config: ServiceConfig) -> FastAPI:
    setup_logging(config)
    app = FastAPI(debug=False)
    app.state.k_recs = config.k_recs

    add_views(app)
    add_middlewares(app)
    add_exception_handlers(app)

    return app
