from collections import Counter
from typing import Dict

import numpy as np
import pandas as pd
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender


class UserKnn:
    """Class for fit-perdict UserKNN model
       based on ItemKNN model from implicit.nearest_neighbours
    """

    def __init__(self, model: ItemItemRecommender, n_neighbors: int = 50):
        self.N_users = n_neighbors
        self.model = model
        self.is_fitted = False

    def get_mappings(self, train):
        self.users_inv_mapping = dict(enumerate(train['user_id'].unique()))
        self.users_mapping = {v: k for k, v in self.users_inv_mapping.items()}

        self.items_inv_mapping = dict(enumerate(train['item_id'].unique()))
        self.items_mapping = {v: k for k, v in self.items_inv_mapping.items()}

    def get_matrix(
        self, df: pd.DataFrame,
        user_col: str = 'user_id',
        item_col: str = 'item_id',
        weight_col: str = None
    ):

        if weight_col:
            weights = df[weight_col].astype(np.float32)
        else:
            weights = np.ones(len(df), dtype=np.float32)

        interaction_matrix = sp.sparse.coo_matrix((
            weights,
            (
                df[user_col].map(self.users_mapping.get),
                df[item_col].map(self.items_mapping.get)
            )
        ))

        self.watched = df.groupby(user_col).agg({item_col: list})
        return interaction_matrix

    def idf(self, n: int, x: float):
        return np.log((1 + n) / (1 + x) + 1)

    def _count_item_idf(self, df: pd.DataFrame):
        item_cnt = Counter(df['item_id'].values)
        item_idf = pd.DataFrame.from_dict(item_cnt, orient='index',
                                          columns=['doc_freq']).reset_index()
        item_idf['idf'] = item_idf['doc_freq'].apply(
            lambda x: self.idf(self.n, x))
        self.item_idf = item_idf

    def fit(self, train: pd.DataFrame):
        self.user_knn = self.model
        self.get_mappings(train)
        self.weights_matrix = self.get_matrix(train)

        self.n = train.shape[0]
        self._count_item_idf(train)

        self.user_knn.fit(self.weights_matrix)
        self.is_fitted = True

    def _generate_recs_mapper(self, model: ItemItemRecommender,
                              user_mapping: Dict[int, int],
                              user_inv_mapping: Dict[int, int], N: int):
        def _recs_mapper(user):
            user_id = user_mapping[user]
            recs = model.similar_items(user_id, N=N)
            mapper = [user_inv_mapping[user] for user, _ in recs], \
                     [sim for _, sim in recs]
            return mapper

        return _recs_mapper

    def predict(self, test: pd.DataFrame, n_recs: int = 10):

        if not self.is_fitted:
            raise ValueError("Please call fit before predict")

        mapper = self._generate_recs_mapper(
            model=self.user_knn,
            user_mapping=self.users_mapping,
            user_inv_mapping=self.users_inv_mapping,
            N=self.N_users
        )

        recs = pd.DataFrame({'user_id': test['user_id'].unique()})
        recs['sim_user_id'], recs['sim'] = zip(*recs['user_id'].map(mapper))
        recs = recs.set_index('user_id').apply(pd.Series.explode).reset_index()

        recs = recs.merge(
            self.watched, left_on=['sim_user_id'], right_on=['user_id'],
            how='left') \
            .explode('item_id') \
            .sort_values(['user_id', 'sim'], ascending=False) \
            .drop_duplicates(['user_id', 'item_id'], keep='first') \
            .merge(self.item_idf, left_on='item_id', right_on='index',
                   how='left')

        recs['score'] = recs['sim'] * recs['idf']
        recs = recs.sort_values(['user_id', 'score'], ascending=False)
        recs['rank'] = recs.groupby('user_id').cumcount() + 1
        predict = recs[recs['rank'] <= n_recs]
        predict = predict[['user_id', 'item_id', 'score', 'rank']]
        return predict


