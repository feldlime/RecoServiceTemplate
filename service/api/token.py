import os

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from service.api.exceptions import NonAuthorizedError

security = HTTPBearer()

SECRET_KEY = os.getenv('SECRET_KEY', '000000')

async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token == SECRET_KEY:
        return None
    else:
        raise NonAuthorizedError()
