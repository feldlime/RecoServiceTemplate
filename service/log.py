import logging.config

from rich.logging import RichHandler
from rich.traceback import install

from .settings import ServiceConfig


def setup_logging(service_config: ServiceConfig):
    logging.basicConfig(
        level=service_config.log_config.level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                enable_link_path=False,
            )
        ],
    )

    logging.getLogger("uvicorn").handlers = logging.getLogger().handlers
    logging.getLogger("gunicorn.error").handlers = logging.getLogger().handlers
    logging.getLogger("gunicorn.access").handlers = logging.getLogger().handlers
    logging.getLogger("fastapi").handlers = logging.getLogger().handlers
    logging.getLogger("uvicorn").handlers = logging.getLogger().handlers
    logging.getLogger("uvicorn.error").handlers = logging.getLogger().handlers
    logging.getLogger("uvicorn.access").handlers = logging.getLogger().handlers

    install()
