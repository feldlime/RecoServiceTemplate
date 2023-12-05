from collections import Counter
from typing import Dict

import numpy as np
import pandas as pd
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender
from annoy import AnnoyIndex

class UserKnn():
    """Class for fit-predict UserKNN model based on ItemKNN model from implicit.nearest_neighbours"""

    def __init__(self, model: ItemItemRecommender, N_users: int = 50, cold_start_recommender=None):
        self.N_users = N_users
        self.model = model
        self.cold_start_recommender = cold_start_recommender
        self.is_fitted = False

    def get_mappings(self, train):
        # Map user and item IDs to internal indices
        self.users_inv_mapping = dict(enumerate(train["user_id"].unique()))
        self.users_mapping = {v: k for k, v in self.users_inv_mapping.items()}

        self.items_inv_mapping = dict(enumerate(train["item_id"].unique()))
        self.items_mapping = {v: k for k, v in self.items_inv_mapping.items()}

    def get_matrix(
        self,
        df: pd.DataFrame,
        user_col: str = "user_id",
        item_col: str = "item_id",
        weight_col: str = None,
        users_mapping: Dict[int, int] = None,
        items_mapping: Dict[int, int] = None,
    ):
        # Generate the interaction matrix (user-item matrix) with optional weights
        if weight_col:
            weights = df[weight_col].astype(np.float64)  # Convert to double
        else:
            weights = np.ones(len(df), dtype=np.float64)  # Use double type

        self.interaction_matrix = sp.sparse.coo_matrix(
            (weights, (df[item_col].map(self.items_mapping.get), df[user_col].map(self.users_mapping.get)))
        )
        # Create a dataframe with watched items for each user
        self.watched = (
            df.groupby(user_col, as_index=False).agg({item_col: list}).rename(columns={user_col: "sim_user_id"})
        )

        return self.interaction_matrix

    def idf(self, n: int, x: float):
        # Inverse Document Frequency (IDF) calculation
        return np.log((1 + n) / (1 + x) + 1)

    def _count_item_idf(self, df: pd.DataFrame):
        # Count item IDF values
        item_cnt = Counter(df["item_id"].values)
        item_idf = pd.DataFrame.from_dict(item_cnt, orient="index", columns=["doc_freq"]).reset_index()
        item_idf["idf"] = item_idf["doc_freq"].apply(lambda x: self.idf(self.n, x))
        self.item_idf = item_idf

    def fit(self, train: pd.DataFrame):
        # Fit the UserKnn model
        self.user_knn = self.model
        self.get_mappings(train)
        self.weights_matrix = self.get_matrix(train, users_mapping=self.users_mapping, items_mapping=self.items_mapping)

        self.n = train.shape[0]
        self._count_item_idf(train)

        # Fit the ItemItemRecommender model
        self.user_knn.fit(self.weights_matrix)
        self.is_fitted = True

    def _generate_recs_mapper(
        self, model: ItemItemRecommender, user_mapping: Dict[int, int], user_inv_mapping: Dict[int, int], N: int
    ):
        # Generate recommendations mapper for similar items
        def _recs_mapper(user):
            try:
                user_id = self.users_mapping[user]
                users, sim = self.user_knn.similar_items(user_id, N=self.N_users)
                return [self.users_inv_mapping[user] for user in users], sim
            except KeyError:
            # Handle missing user ID (e.g., return default recommendations)
                return [], []

        return _recs_mapper

    def predict(self, test: pd.DataFrame, N_recs: int = 10):
        # Make recommendations for test users
        if not self.is_fitted:
            raise ValueError("Please call fit before predict")

        mapper = self._generate_recs_mapper(
            model=self.user_knn,
            user_mapping=self.users_mapping,
            user_inv_mapping=self.users_inv_mapping,
            N=self.N_users,
        )

        recs = pd.DataFrame({"user_id": test["user_id"].unique()})
        recs["sim_user_id"], recs["sim"] = zip(*recs["user_id"].map(mapper))
        recs = recs.set_index("user_id").apply(pd.Series.explode).reset_index()

        recs = (
            recs[~(recs["user_id"] == recs["sim_user_id"])]
            .merge(self.watched, on=["sim_user_id"], how="left")
            .explode("item_id")
            .sort_values(["user_id", "sim"], ascending=False)
            .drop_duplicates(["user_id", "item_id"], keep="first")
            .merge(self.item_idf, left_on="item_id", right_on="index", how="left")
        )

        recs["score"] = recs["sim"] * recs["idf"]
        recs = recs.sort_values(["user_id", "score"], ascending=False)
        recs["rank"] = recs.groupby("user_id").cumcount() + 1

        # Handle cold-start users
        cold_start_users = test[~test["user_id"].isin(self.users_inv_mapping)]
        if not cold_start_users.empty and self.cold_start_recommender:
            cold_start_recs = self.cold_start_recommender.predict(cold_start_users, N_recs)
            recs = pd.concat([recs, cold_start_recs], ignore_index=True)

        # Task 1.3 : Make recommendations for cold-start users using the cold_start_recommender
        return recs[recs["rank"] <= N_recs][["user_id", "item_id", "score", "rank"]]

    def recommendation(self, user_id: int, N_recs: int = 10):
        df = pd.DataFrame({"user_id": [user_id], "item_id": [user_id]})
        return self.predict(df, N_recs=N_recs).item_id.to_list()
    
import os
import pickle

class Pickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'UserKnn': 
            return UserKnn
        return super().find_class(module, name)
    
def load(path:str):
        with open(os.path.join(path), 'rb') as f:
            return Pickler(f).load()