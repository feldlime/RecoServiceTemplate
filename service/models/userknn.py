from typing import Optional

import numpy as np
import pandas as pd
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender


class UserKnn:  # pylint: disable=too-many-instance-attributes
    """
    Class for fit-predict UserKNN model and BM25
    based on ItemKNN model from implicit.nearest_neighbours
    """

    def __init__(
        self,
        dist_model: ItemItemRecommender,
        n_neighbors: int = 50,
        verbose: int = 1,
    ) -> None:
        self.n_neighbors = n_neighbors
        self.dist_model = dist_model
        self.is_fitted = False
        self.verbose = verbose

        self.users_inv_mapping: Optional[dict[int, int]] = None
        self.users_mapping: Optional[dict[int, int]] = None
        self.items_inv_mapping: Optional[dict[int, int]] = None
        self.items_mapping: Optional[dict[int, int]] = None
        self.weights_matrix = None
        self.users_watched = None

    def get_mappings(self, train) -> None:
        self.users_inv_mapping = dict(enumerate(train['user_id'].unique()))
        self.users_mapping = {v: k for k, v in self.users_inv_mapping.items()}

        self.items_inv_mapping = dict(enumerate(train['item_id'].unique()))
        self.items_mapping = {v: k for k, v in self.items_inv_mapping.items()}

    def get_matrix(
        self, df: pd.DataFrame,
        user_col: str = 'user_id',
        item_col: str = 'item_id',
        weight_col: str = None,
    ):
        if weight_col:
            weights = df[weight_col].astype(np.float32)
        else:
            weights = np.ones(len(df), dtype=np.float32)

        interaction_matrix = sp.sparse.coo_matrix((
            weights,
            (
                df[user_col].map(self.users_mapping.get),  # type: ignore
                df[item_col].map(self.items_mapping.get)  # type: ignore
            )
        ))

        self.users_watched = df.groupby(user_col).agg({item_col: list})
        return interaction_matrix.tocsr().T

    def fit(self, train: pd.DataFrame) -> None:
        self.get_mappings(train)
        self.weights_matrix = self.get_matrix(train)

        self.dist_model.fit(
            self.weights_matrix,
            show_progress=(self.verbose > 0)
        )
        self.is_fitted = True

    @staticmethod
    def _generate_recs_mapper(
        model: ItemItemRecommender,
        user_mapping: Optional[dict[int, int]],
        user_inv_mapping: Optional[dict[int, int]],
        n_neighbors: int
    ):
        def _recs_mapper(user):
            user_id = user_mapping[user]
            recs = model.similar_items(user_id, N=n_neighbors)
            return (
                [user_inv_mapping[user] for user, _ in zip(*recs)],
                [sim for _, sim in zip(*recs)]
            )
        return _recs_mapper

    def predict_user(self, user_id: int, n_recs: int = 10) -> list[int]:
        recs = pd.DataFrame({'user_id': [user_id]})
        predict = self.predict(recs=recs, n_recs=n_recs)
        return predict

    def predict(self, recs: pd.DataFrame, n_recs: int = 10) -> list[int]:

        if not self.is_fitted:
            raise ValueError("Fit model before predicting")

        mapper = self._generate_recs_mapper(
            model=self.dist_model,
            user_mapping=self.users_mapping,
            user_inv_mapping=self.users_inv_mapping,
            n_neighbors=self.n_neighbors
        )

        try:
            recs['sim_user_id'], recs['sim'] = zip(
                *recs['user_id'].map(mapper)
            )
        except BaseException:  # pylint: disable=broad-except
            return []

        recs = recs.set_index('user_id').apply(pd.Series.explode).reset_index()

        recs = (
            recs
            .merge(
                self.users_watched,
                left_on=['sim_user_id'],
                right_on=['user_id'],
                how='left'
            )
            .explode('item_id')
            .drop_duplicates(['user_id', 'item_id'], keep='first')
            .sort_values(['user_id', 'sim'], ascending=False)
        )

        recs['rank'] = recs.groupby('user_id').cumcount() + 1

        result = recs[recs['rank'] <= n_recs][['user_id', 'item_id', 'rank']]
        predict = result.item_id.tolist()[:n_recs]
        return predict
