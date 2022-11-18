from abc import ABC, abstractmethod
from typing import Dict, List, Type
import random


class RecModel(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def preparing(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_answer(self, *args, **kwargs) -> List[int]:
        return list(range(kwargs['k_recs']))


class RandomModel(RecModel):
    def preparing(self, *args, **kwargs) -> None:
        pass

    def get_answer(self, *args, **kwargs) -> List[int]:
        random.seed(kwargs['user_id'])
        return random.sample(range(0, 256), kwargs['k_recs'])


all_models: Dict[str, Type[RecModel]] = {
    'random_model': RandomModel
}
