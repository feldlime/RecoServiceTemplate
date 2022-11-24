from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")

BEARER_TOKEN_DEPS = Depends(OAUTH2_SCHEME)
