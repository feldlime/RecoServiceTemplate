
from http import HTTPStatus
import yaml

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

with open('config/config_service.yml') as stream:
    config = yaml.safe_load(stream)['config']


def verify_jwt(token: str) -> bool:
    is_token_valid: bool = False

    if token == config['token']:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                    detail="Invalid authentication scheme :( ")
            if not verify_jwt(credentials.credentials):
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                    detail="Invalid token or it is expired :( ")
            return credentials.credentials
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="Invalid authorization code :( ")
