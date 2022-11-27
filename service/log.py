import logging.config
import typing as tp

from .settings import ServiceConfig

app_logger = logging.getLogger("app")
access_logger = logging.getLogger("access")


class ServiceNameFilter(logging.Filter):
    def __init__(self, name: str = "", service_name: str = "") -> None:
        self.service_name = service_name

        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, "service_name", self.service_name)

        return super().filter(record)


def get_config(service_config: ServiceConfig) -> tp.Dict[str, tp.Any]:
    level = service_config.log_config.level
    datetime_format = service_config.log_config.datetime_format

    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "loggers": {
            "root": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            app_logger.name: {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            access_logger.name: {
                "level": level,
                "handlers": ["access"],
                "propagate": False,
            },
            "gunicorn.error": {
                "level": "INFO",
                "handlers": [
                    "console",
                ],
                "propagate": False,
            },
            "gunicorn.access": {
                "level": "ERROR",
                "handlers": [
                    "gunicorn.access",
                ],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": [
                    "console",
                ],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "ERROR",
                "handlers": [
                    "gunicorn.access",
                ],
                "propagate": False,
            },
        },
        "handlers": {
            "console": {
                "formatter": "console",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["service_name"],
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["service_name"],
            },
            "gunicorn.access": {
                "class": "logging.StreamHandler",
                "formatter": "gunicorn.access",
                "stream": "ext://sys.stdout",
                "filters": ["service_name"],
            },
        },
        "formatters": {
            "console": {
                "format": (
                    'time="%(asctime)s" '
                    'level="%(levelname)s" '
                    'service_name="%(service_name)s" '
                    'logger="%(name)s" '
                    'pid="%(process)d" '
                    'message="%(message)s" '
                ),
                "datefmt": datetime_format,
            },
            "access": {
                "format": (
                    'time="%(asctime)s" '
                    'level="%(levelname)s" '
                    'service_name="%(service_name)s" '
                    'logger="%(name)s" '
                    'pid="%(process)d" '
                    'method="%(method)s" '
                    'requested_url="%(requested_url)s" '
                    'status_code="%(status_code)s" '
                    'request_time="%(request_time)s" '
                ),
                "datefmt": datetime_format,
            },
            "gunicorn.access": {
                "format": (
                    'time="%(asctime)s" '
                    'level="%(levelname)s" '
                    'logger="%(name)s" '
                    'pid="%(process)d" '
                    '"%(message)s"'
                ),
                "datefmt": datetime_format,
            },
        },
        "filters": {
            "service_name": {
                "()": "service.log.ServiceNameFilter",
                "service_name": service_config.service_name,
            },
        },
    }

    return config


def setup_logging(service_config: ServiceConfig) -> None:
    config = get_config(service_config)
    logging.config.dictConfig(config)
