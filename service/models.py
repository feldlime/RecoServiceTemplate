import typing as tp

from pydantic import BaseModel


class Error(BaseModel):
    error_key: str
    error_message: str
    error_loc: tp.Optional[tp.Any] = None


class User(BaseModel):
    username: str
    email: tp.Union[str, None] = None
    full_name: tp.Union[str, None] = None
    disabled: tp.Union[bool, None] = None


class UserInDB(User):
    hashed_password: str
