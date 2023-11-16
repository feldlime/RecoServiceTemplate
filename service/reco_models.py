from abc import ABC, abstractmethod
from typing import List


class BaseModel(ABC):
    @abstractmethod
    def get_reco(self, user_id: int, k_recs: int):
        pass


class DummyModel(BaseModel):
    def get_reco(self, user_id: int, k_recs: int) -> List[int]:
        return list(range(k_recs))


models_dict = {"dummy_model": DummyModel()}
