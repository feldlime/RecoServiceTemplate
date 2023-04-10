from typing import List, Optional, Sequence

from pydantic import BaseModel


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]

class NotFoundError(BaseModel):
    error_key: str
    error_message: str = "NotFound"
    error_loc: Optional[Sequence[str]]


class UnauthorizedError(BaseModel):
    error_key: str
    error_message: str = "Unauthorized"
    error_loc: Optional[Sequence[str]]
