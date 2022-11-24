import random
from typing import List

from .base_model import BaseModel
from .common import register_model


@register_model("random_number_model")
class RandomNumberModel(BaseModel):
    def __init__(self, min_int: int = 0, max_int: int = 10000):
        self.min_int = min_int
        self.max_int = max_int

    def predict(self, user_id, k_recs: int = 100) -> List[int]:
        del user_id
        return random.sample(range(self.min_int, self.max_int+1), k_recs)
