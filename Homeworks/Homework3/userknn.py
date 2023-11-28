from typing import Dict
from collections import Counter

import pandas as pd
import numpy as np
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender


class UserKnn():
    """Class for fit-perdict UserKNN model 
       based on ItemKNN model from implicit.nearest_neighbours
    """
    
    def __init__(self, model: ItemItemRecommender, N_users: int = 50):
        self.N_users = N_users
        self.model = model
        self.is_fitted = False
        
    def get_mappings(self, train):
        self.users_inv_mapping = dict(enumerate(train['user_id'].unique()))
        self.users_mapping = {v: k for k, v in self.users_inv_mapping.items()}
        
        self.items_inv_mapping = dict(enumerate(train['item_id'].unique()))
        self.items_mapping = {v: k for k, v in self.items_inv_mapping.items()}
    
    def get_matrix(self, df: pd.DataFrame, 
                   user_col: str = 'user_id', 
                   item_col: str = 'item_id', 
                   weight_col: str = None, 
                   users_mapping: Dict[int, int] = None, 
                   items_mapping: Dict[int, int] = None):
    
        if weight_col:
            weights = df[weight_col].astype(np.float32)
        else:
            weights = np.ones(len(df), dtype=np.float32)

        self.interaction_matrix = sp.sparse.coo_matrix((
            weights, 
            (
                df[item_col].map(self.items_mapping.get),
                df[user_col].map(self.users_mapping.get)
            )
            ))
        
        self.watched = df\
            .groupby(user_col, as_index=False)\
            .agg({item_col: list})\
            .rename(columns={user_col: 'sim_user_id'})
        
        return self.interaction_matrix
        
    def idf(self, n: int, x: float):
        return np.log((1 + n) / (1 + x) + 1)
        
    def _count_item_idf(self, df: pd.DataFrame):
        item_cnt = Counter(df['item_id'].values)
        item_idf = pd.DataFrame.from_dict(item_cnt, orient='index', 
                                          columns=['doc_freq']).reset_index()
        item_idf['idf'] = item_idf['doc_freq'].apply(lambda x: self.idf(self.n, x))
        self.item_idf = item_idf 
    
    def fit(self, train: pd.DataFrame):
        self.user_knn = self.model
        self.get_mappings(train)
        self.weights_matrix = self.get_matrix(train, 
                                              users_mapping=self.users_mapping, 
                                              items_mapping=self.items_mapping)
        
        self.n = train.shape[0]
        self._count_item_idf(train)
        
        self.user_knn.fit(self.weights_matrix)
        self.is_fitted = True

    def _generate_recs_mapper(self, model: ItemItemRecommender, user_mapping: Dict[int, int], 
                              user_inv_mapping: Dict[int, int], N: int):
        def _recs_mapper(user):
            user_id = self.users_mapping[user]
            users, sim = model.similar_items(user_id, N=N)
            return [self.users_inv_mapping[user] for user in users], sim
        return _recs_mapper
    
    def predict(self, test: pd.DataFrame, N_recs: int = 10):
        
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
        
        recs = recs[~(recs['user_id'] == recs['sim_user_id'])]\
            .merge(self.watched, on=['sim_user_id'], how='left')\
            .explode('item_id')\
            .sort_values(['user_id', 'sim'], ascending=False)\
            .drop_duplicates(['user_id', 'item_id'], keep='first')\
            .merge(self.item_idf, left_on='item_id', right_on='index', how='left')
        
        recs['score'] = recs['sim'] * recs['idf']
        recs = recs.sort_values(['user_id', 'score'], ascending=False)
        recs['rank'] = recs.groupby('user_id').cumcount() + 1 
        return recs[recs['rank'] <= N_recs][['user_id', 'item_id', 'score', 'rank']]
    