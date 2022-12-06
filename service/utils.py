from service.api.exceptions import InvalidTokenError


def verify_token(expected, token):
    if expected != token:
        raise InvalidTokenError()
