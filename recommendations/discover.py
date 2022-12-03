import importlib.util
import inspect
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import (
    Dict,
    Type,
)

from recommendations.estimator import Estimator

log = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def discover_models() -> Dict[str, Type]:
    """Discover all models in model path"""

    models_directory = Path(__file__).parent.joinpath("models")
    estimators = {}

    for path in models_directory.glob("*.py"):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec:
            log.warning(f"Cannot import {path}")
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore

        for estimator in filter(
            lambda x: isinstance(x, Estimator),
            (
                obj[1]
                for obj in inspect.getmembers(module, inspect.isclass)
                if obj[1].__module__ == module.__name__
            ),
        ):
            log.info(
                f"Found estimator `{estimator.name}` ({estimator.__class__.__name__})"
            )
            estimators[estimator.name] = estimator

    return estimators
