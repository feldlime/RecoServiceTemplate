from abc import ABC, abstractmethod
from collections import defaultdict
from functools import reduce
from typing import Dict, List, Optional, Set, Tuple

import dill
import numpy as np
import pandas as pd
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender
from lightfm import LightFM
from scipy.sparse import csr_matrix


class BaseModelZoo(ABC):
    def __init__(self):
        pass

    @staticmethod
    def unique_reco(items: List[int]) -> List[int]:
        seen: Set[int] = set()
        seen_add = seen.add
        return [item for item in items if not (item in seen or seen_add(item))]

    @abstractmethod
    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """


class DumpModel(BaseModelZoo):
    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """
        reco = list(range(k_recs))
        return reco


class TopPopularAllCovered(BaseModelZoo):
    def __init__(
        self,
        top_reco: Tuple[int, ...] = tuple([
            10440, 15297, 9728, 13865, 2657,
            4151, 3734, 6809, 4740, 4880, 7571,
            11237, 8636, 14741
        ])
    ) -> None:
        super().__init__()
        self.top_reco = top_reco

    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """
        reco = list(self.top_reco)[:k_recs]
        return reco


class Popular(BaseModelZoo):
    def __init__(
        self,
        top_reco: Tuple[int, ...] = tuple([
            10440, 15297, 9728, 13865, 4151,
            3734, 2657, 4880, 142, 6809
        ])
    ) -> None:
        super().__init__()
        self.top_reco = top_reco

    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """
        reco = list(self.top_reco)[:k_recs]
        return reco


class KNNModelWithTop(BaseModelZoo):
    def __init__(
        self,
        path_to_reco: str = "data/BlendingKNNWithAddFeatures.csv.gz",
        top_reco: Tuple[int, ...] = tuple([
            10440, 15297, 9728, 13865, 3734,
            12192, 4151, 11863, 7793, 7829
        ]),
    ) -> None:
        super().__init__()
        self.path_to_reco = path_to_reco
        if self.path_to_reco.endswith('csv.gz'):
            self.data = pd.read_csv(path_to_reco, compression='gzip')
        elif self.path_to_reco.endswith('.csv'):
            self.data = pd.read_csv(path_to_reco)
        self.top_reco = top_reco

    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """
        reco = (
            self.data[self.data.user_id == user_id]
            .item_id
            .tolist()
            [:k_recs]
        )

        if len(reco) < k_recs:
            reco.extend(self.top_reco)
            reco = self.unique_reco(reco)[:k_recs]  # Удаляем дубли

        return reco


class OnlineModel(BaseModelZoo):
    def __init__(
        self,
        path_to_model: str = "data/knn_bm25.pickle",
        top_reco: Tuple[int, ...] = tuple([
            10440, 15297, 9728, 13865, 3734,
            12192, 4151, 11863, 7793, 7829
        ])
    ) -> None:
        super().__init__()

        with open(path_to_model, 'rb') as f:
            self.model = dill.load(f)

        self.top_reco = top_reco

    def reco_predict(
        self,
        user_id: int,
        k_recs: int
    ) -> List[int]:
        """
        Main function for recommendation items to users
        :param user_id: user identification
        :param k_recs: how many recs do you need
        :return: list of recommendation ids
        """
        try:
            reco = self.model.predict(user_id=user_id)
        except KeyError:
            reco = []

        if len(reco) < k_recs:
            reco.extend(self.top_reco)
            reco = self.unique_reco(reco)[:k_recs]  # Удаляем дубли

        return reco


class UserKNN:
    """
    Class for fit-perdict UserKNN model and BM25
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

    @staticmethod
    def _generate_recs_mapper(
        model: ItemItemRecommender,
        user_mapping: Dict[int, int],
        user_inv_mapping: Dict[int, int],
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


class LightFMWrapper:
    """
    Class for fit-predict LightFM
    """
    def __init__(
        self,
        random_state: int = 42,
        learning_rate: float = 0.05,
        no_components: int = 10,
        item_alpha: float = 0,
        user_alpha: float = 0,
        loss: str = 'warp',
    ):

        self.is_fitted = False

        self.mapping: Dict[str, Dict[int, int]] = defaultdict(dict)

        self.weights_matrix = None
        self.users_watched = None

        self.user_features = None
        self.item_features = None

        self.model = LightFM(
            loss=loss,
            no_components=no_components,
            user_alpha=user_alpha,
            item_alpha=item_alpha,
            random_state=random_state,
            learning_rate=learning_rate,
        )

    def get_mappings(self, users, items):
        self.mapping['users_inv_mapping'] = dict(
            enumerate(users['user_id'].unique())
        )
        self.mapping['users_mapping'] = dict({
            v: k for k, v in self.mapping['users_inv_mapping'].items()
        })

        self.mapping['items_inv_mapping'] = dict(
            enumerate(items['item_id'].unique())
        )
        self.mapping['items_mapping'] = dict({
            v: k for k, v in self.mapping['items_inv_mapping'].items()
        })

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

    def prepare_additional_features_users(self, features: pd.DataFrame):
        user_features_frames = []
        for feature in ["sex", "age", "income"]:
            feature_frame = features.reindex(columns=['user_id', feature])
            feature_frame.columns = ["id", "value"]
            feature_frame["feature"] = feature
            user_features_frames.append(feature_frame)
        user_features = pd.concat(user_features_frames)

        user_final_features = pd.get_dummies(
            user_features[['id', 'value']]).groupby('id', as_index=False).sum()

        user_final_features.id = user_final_features.id.map(
            self.mapping['items_mapping']
        )
        user_final_features = user_final_features.sort_values('id').drop(
            'id',
            axis=1
        )
        user_final_features = csr_matrix(user_final_features.values)

        return user_final_features

    def prepare_additional_features_items(self, features: pd.DataFrame):
        features.fillna('Unknown', inplace=True)
        features["genre"] = features["genres"].str.lower().str.replace(
            ", ",
            ",",
            regex=False
        ).str.split(",")
        features["actors"] = features["actors"].str.lower().str.replace(
            ", ",
            ",",
            regex=False
        ).str.split(",")

        genre_feature = features[["item_id", "genre"]].explode("genre")
        genre_feature.columns = ["id", "value"]
        genre_feature["feature"] = "genre"

        actors_feature = features[["item_id", "actors"]].explode("actors")
        actors_feature.columns = ["id", "value"]
        actors_feature["feature"] = "actors"

        content_feature = features.reindex(columns=['item_id', "content_type"])
        content_feature.columns = ["id", "value"]
        content_feature["feature"] = "content_type"

        country_feature = features.reindex(columns=['item_id', "countries"])
        country_feature.columns = ["id", "value"]
        country_feature["feature"] = "countries"

        age_feature = features.reindex(columns=['item_id', "age_rating"])
        age_feature.columns = ["id", "value"]
        age_feature["feature"] = "age_feature"

        studios_feature = features.reindex(columns=['item_id', "studios"])
        studios_feature.columns = ["id", "value"]
        studios_feature["feature"] = "studios"

        genre_feature_bin = (
            pd.get_dummies(genre_feature[['id', 'value']])
            .groupby('id', as_index=False)
            .sum()
        )
        content_feature_bin = (
            pd.get_dummies(content_feature[['id', 'value']])
            .groupby('id', as_index=False)
            .sum()
        )
        studios_feature_bin = (
            pd.get_dummies(studios_feature[['id', 'value']])
            .groupby('id', as_index=False)
            .sum()
        )
        age_feature_bin = (
            pd.get_dummies(age_feature[['id', 'value']])
            .groupby('id', as_index=False)
            .sum()
        )
        country_feature_bin = (
            pd.get_dummies(country_feature[['id', 'value']])
            .groupby('id', as_index=False)
            .sum()
        )

        dfs = [
            genre_feature_bin,
            content_feature_bin,
            studios_feature_bin,
            age_feature_bin,
            country_feature_bin
        ]
        item_final_features = reduce(
            lambda left, right: pd.merge(left, right, on='id'),
            dfs
        )

        item_final_features.id = item_final_features.id.map(
            self.mapping['items_mapping']
        )
        item_final_features = (
            item_final_features
            .sort_values('id')
            .drop('id', axis=1)
        )
        item_final_features_matrix_sparse = csr_matrix(
            item_final_features.values)

        return item_final_features_matrix_sparse

    def fit(
        self,
        train: pd.DataFrame,
        user_features: Optional[pd.DataFrame] = None,
        # если не none, то делаем фичи
        item_features: Optional[pd.DataFrame] = None,
        # если не none, то делаем фичи
        epochs: int = 1,
        num_threads: int = 8,
        verbose: int = 1,

    ):
        if user_features is not None:
            self.user_features = self.prepare_additional_features_users(
                user_features)

        if item_features is not None:
            self.item_features = self.prepare_additional_features_items(
                item_features)

        self.get_mappings(user_features, item_features)
        self.weights_matrix = self.get_matrix(train).tocsr()

        self.model.fit(
            self.weights_matrix,
            epochs=epochs,
            user_features=self.user_features,
            # csr_matrix of shape [n_users, n_user_features]
            item_features=self.item_features,
            # csr_matrix of shape [n_items, n_item_features]
            num_threads=num_threads,
            verbose=verbose > 0,
        )

        self.is_fitted = True

    def predict(self, user_id: int, n_recs: int = 10):

        if not self.is_fitted:
            raise ValueError("Fit model before predicting")

        if user_id not in self.mapping['users_mapping'].keys():
            return []
        user_id = self.mapping['users_mapping'][user_id]

        scores = self.model.predict(
            user_id,
            np.arange(len(self.mapping['items_mapping'])),
            item_features=self.item_features,
            user_features=self.user_features
        )  # LightFM
        top_items = np.argsort(-scores)[:n_recs]
        reco = [
            self.mapping['items_inv_mapping'][inv_reco_item]
            for inv_reco_item in top_items
        ]

        return reco
