import pandas as pd
import numpy as np
import scipy as sp
from typing import Dict
from collections import defaultdict
from collections import Counter
import implicit
from implicit.nearest_neighbours import ItemItemRecommender


class UserKnn():
    """Class for fit-perdict UserKNN model
       based on ItemKNN model from implicit.nearest_neighbours
    """

    def __init__(
            self,
            dist_model: ItemItemRecommender,
            n_neighbors: int = 50,
            verbose: int = 1,
    ):
        self.n_neighbors = n_neighbors
        self.dist_model = dist_model
        self.verbose = verbose
        self.is_fitted = False

        self.mapping: Dict[str, Dict[int, int]] = defaultdict(dict)

        self.weights_matrix = None
        self.users_watched = None

    def get_mappings(self, train):
        self.mapping['users_inv_mapping'] = dict(
            enumerate(train['user_id'].unique())
        )
        self.mapping['users_mapping'] = {
            v: k for k, v in self.mapping['users_inv_mapping'].items()
        }

        self.mapping['items_inv_mapping'] = dict(
            enumerate(train['item_id'].unique())
        )
        self.mapping['items_mapping'] = {
            v: k for k, v in self.mapping['items_inv_mapping'].items()
        }

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

        if hasattr(self.mapping['users_mapping'], 'get') and \
                hasattr(self.mapping['items_mapping'], 'get'):
            interaction_matrix = sp.sparse.coo_matrix((
                weights,
                (
                    df[user_col].map(self.mapping['users_mapping'].get),
                    df[item_col].map(self.mapping['items_mapping'].get)
                )
            ))
        else:
            raise AttributeError

        self.users_watched = df.groupby(user_col).agg({item_col: list})
        return interaction_matrix

    def fit(self, train: pd.DataFrame):
        self.get_mappings(train)
        self.weights_matrix = self.get_matrix(train).tocsr().T

        self.dist_model.fit(
            self.weights_matrix,
            show_progress=(self.verbose > 0)
        )
        self.is_fitted = True

    def _generate_recs_mapper(self, model: ItemItemRecommender, user_mapping: Dict[int, int],
                              user_inv_mapping: Dict[int, int], n_neighbors: int):
        def _recs_mapper(user):
            user_id = user_mapping[user]
            recs = model.similar_items(user_id, N=n_neighbors)
            return [user_inv_mapping[user] for user, _ in recs], [sim for _, sim in recs]
        return _recs_mapper

    def predict(self, user_id: int, n_recs: int = 10):

        if not self.is_fitted:
            raise ValueError("Fit model before predicting")

        mapper = self._generate_recs_mapper(
            model=self.dist_model,
            user_mapping=self.mapping['users_mapping'],
            user_inv_mapping=self.mapping['users_inv_mapping'],
            n_neighbors=self.n_neighbors
        )

        recs = pd.DataFrame({'user_id': [user_id]})

        try:
            recs['sim_user_id'], recs['sim'] = zip(
                *recs['user_id'].map(mapper)
            )
        except AttributeError:
            return []

        recs = recs.set_index('user_id').apply(pd.Series.explode).reset_index()

        recs = (
            recs
            .merge(
                self.users_watched,
                left_on=['sim_user_id'],
                right_on=['user_id'], how='left'
            )
            .explode('item_id')
            .sort_values(['user_id', 'sim'], ascending=False)
            .drop_duplicates(['user_id', 'item_id'], keep='first')
        )

        recs['rank'] = recs.groupby('user_id').cumcount() + 1

        result = recs[recs['rank'] <= n_recs][['user_id', 'item_id', 'rank']]

        return result.item_id.tolist()[:n_recs]