from typing import List

from service.recmodels.base_model import RecsysBaseModel


class RandomModel(RecsysBaseModel):
    """Return random sequence
    """
    def get_items_reco(self, user_id: int, size: int = 10) -> List[int]:
        return [i for i in range(size)]
