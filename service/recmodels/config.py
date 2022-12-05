from typing import Dict

from service.recmodels.base_model import RecsysBaseModel
from service.recmodels.radom_model import RandomModel


def init_config() -> Dict[str, RecsysBaseModel]:
    """Init all relevant models

    Returns:
        Dict[str, RecsysBaseModel]: model name to concrete model
    """
    return {
        'random': RandomModel(''),
    }
