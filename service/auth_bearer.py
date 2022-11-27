import os

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.token_template = os.environ.get("JWT_TOKEN", None)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = \
            await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=401,
                                    detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403,
                                    detail="Invalid token.")
            return credentials.credentials
        raise HTTPException(status_code=403,
                            detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        return self.token_template == token
