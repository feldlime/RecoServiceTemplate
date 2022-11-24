from typing import Dict, Type

from service.api.exceptions import RegisterModelError

from .base_model import BaseModel

MODELS: Dict[str, Type[BaseModel]] = {}


def register_model(name: str):
    def register(cls: Type[BaseModel]) -> Type[BaseModel]:
        if not issubclass(cls, BaseModel):
            raise RegisterModelError(cls, name)
        MODELS[name] = cls
        return cls

    return register
