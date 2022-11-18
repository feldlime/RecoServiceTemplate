import os

from jose import jwt
from jose.exceptions import JOSEError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from service.api.exceptions import NonAuthorizedError

security = HTTPBearer()

SECRET_KEY = os.getenv('SECRET_KEY', '7c2de62e1c23556420b0d05ea3b3543d28048ce14bfed57131ca4b9643081609')


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
    except JOSEError as e:
        raise NonAuthorizedError()
