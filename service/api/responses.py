from pydantic import BaseModel

from .exceptions import (
    ModelNotFoundError,
    NotAuthorizedError,
    UserNotFoundError,
)

responses = {
    "200": {
        "description": 'Success',
        "content": {
            "application/json": {
                "example":
                    BaseModel()

            }
        }
    },
    "404": {
        "description": 'Error: Model or User not found',
        "content": {
            "application/json": {
                "example":
                    (
                        ModelNotFoundError(),
                        UserNotFoundError(),
                    )

            }
        }
    },
    "401": {
        "description": 'Error: Not Authorized',
        "content": {
            "application/json": {
                "example":
                    NotAuthorizedError()

            }
        }
    },
}
