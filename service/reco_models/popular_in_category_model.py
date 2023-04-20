from typing import Any, Dict, List, Set

import dill


class PopularInCategory:
    """This class is implementation of recommendations generation with
    popular model by user category

    Parameters
    ----------
    model_path: str
        Path to dilled model
    """

    __slots__ = {"model"}

    def __init__(self, model_path: str):
        try:
            with open(model_path, "rb") as file:
                self.model: Dict[str, Any] = dill.load(file)
        except FileNotFoundError as e:
            print(f"ERROR while loading model: {e}" f"\nRun `make load_models` to load model from GDrive")

    def predict(self, user_id: int, k: int) -> List[int]:
        """Returns top k items for specific user_id

        :param user_id: int
            User's ID from KION dataset
        :param k: int
            Number of item_ids for that user_id
        :return: List[int]
            Returns k item_ids
        """
        user_to_watched_items_map: Dict[int, Set[int]] = self.model["user_to_watched_items_map"]
        user_to_category_map: Dict[int, str] = self.model["user_to_category_map"]
        category_to_popular_recs: Dict[str, List[int]] = self.model["category_to_popular_recs"]

        watched_items = set()
        if user_id in user_to_watched_items_map:
            watched_items = user_to_watched_items_map[user_id]

        user_category = "default"
        if user_id in user_to_category_map:
            user_category = user_to_category_map[user_id]

        recs_for_user_category = category_to_popular_recs[user_category]
        result = []
        current_recs_in_result = 0
        for item_id in recs_for_user_category:
            if item_id not in watched_items:
                result.append(item_id)
                current_recs_in_result += 1
            if current_recs_in_result == k:
                return result

        recs_default = category_to_popular_recs["default"]
        for item_id in recs_default:
            if item_id not in watched_items and item_id not in result:
                result.append(item_id)
                current_recs_in_result += 1
            if current_recs_in_result == k:
                return result
        return result + [item_id + 1 for item_id in range(k - len(result))]
