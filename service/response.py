import json
import typing as tp
from http import HTTPStatus

import orjson
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from service.models import Error


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: tp.Any) -> tp.Any:
        if isinstance(o, BaseModel):
            return o.dict()
        try:
            orjson.dumps(o)
        except TypeError:
            return str(o)
        return super().default(o)


class DataclassJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: tp.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=EnhancedJSONEncoder,
        ).encode("utf-8")


def create_response(
    status_code: int,
    message: tp.Optional[str] = None,
    data: tp.Optional[tp.Any] = None,
    errors: tp.Optional[tp.List[Error]] = None,
) -> JSONResponse:
    content: tp.Dict[str, tp.Any] = {}

    if message is not None:
        content["message"] = message

    if data is not None:
        content["data"] = data

    if errors is not None:
        content["errors"] = errors

    return DataclassJSONResponse(content, status_code=status_code)


def server_error(errors: tp.List[Error]) -> JSONResponse:
    return create_response(HTTPStatus.INTERNAL_SERVER_ERROR, errors=errors)
