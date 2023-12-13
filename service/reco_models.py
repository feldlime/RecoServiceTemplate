import os
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List

WEIGHTS_PATH = "./models/weights"


class BaseModel(ABC):
    @abstractmethod
    def get_reco(self, user_id: int, k_recs: int):
        pass


class DummyModel(BaseModel):
    def get_reco(self, user_id: int, k_recs: int) -> List[int]:
        return list(range(k_recs))


class AnnModel(BaseModel):
    def __init__(self) -> None:
        super().__init__()
        with open(os.path.join(WEIGHTS_PATH, "ann_model.pkl"), "rb") as file:
            self.model = pickle.load(file)

    def get_reco(self, user_id: int, k_recs: int) -> List[int]:
        recos = self.model.recommend_single(user_id, k_recs)
        return list(recos)


def get_models(is_test: bool) -> Dict[Any, Any]:
    if is_test:
        return {"dummy_model": DummyModel()}
    return {"ann_model": AnnModel(), "dummy_model": DummyModel()}
