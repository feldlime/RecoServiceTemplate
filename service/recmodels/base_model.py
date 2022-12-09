from abc import ABC, abstractmethod
from typing import List


class RecsysBaseModel(ABC):
    """Abstract interface for mode

    Raises:
        NotImplementedError: if abstract method is not implemented
    """

    def __init__(self, path_to_model: str) -> None:
        """Init model

        Args:
            path_to_model (str): path to model to init
        """
        self._path_to_model = path_to_model

    @abstractmethod
    def get_items_reco(self, user_id: int, size: int = 10) -> List[int]:
        """Return recs list for user id

        Args:
            user_id (int): users ID
            size (int): size of recs list

        Returns:
            List[int]: Recs list for user ID
        """
        raise NotImplementedError()
