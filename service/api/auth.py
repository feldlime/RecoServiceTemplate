import os

from dotenv import load_dotenv

from .exceptions import InvalidAuthorization

load_dotenv()


def check_access(authorization: str):
    if authorization is None:
        raise InvalidAuthorization(error_message="No token")
    token = authorization.split(" ")[-1]
    secret_key = os.getenv("SECRET_KEY")
    print(secret_key)
    if token != secret_key:
        raise InvalidAuthorization(error_message="Invalid token")
