import os
import pickle
from collections import Counter

import dill
import numpy as np
import pandas as pd
from rectools.dataset import Dataset

from service.api.exceptions import NotEnoughError
from service.models.utils import make_dataset


class RangeTest:
    def __init__(self):
        pass

    @staticmethod
    def recommend(_):
        reco = list(range(10))

        return reco


class UserKnn:
    """Class for fit-perdict UserKNN model
    """

    def __init__(self, model_path: str, nn: int = 50):
        with open(model_path, 'rb') as fh:
            self.model = dill.load(fh)
        self.dataset, _, _ = make_dataset()
        self.idf, self.idf_dict = self.prepare_idf()

        train_ids = np.load("service/models/weights/train_ids.npy",
                            allow_pickle=True)
        train = self.dataset.loc[train_ids]
        self.dataset = train

        self.watched, self.watched_dict = self.prepare_watched()

        self.get_mappings(train)

        self.mapper = self._generate_recs_mapper(N=nn)

    def recommend(self, user_id: int):
        pred_df = pd.DataFrame({
            'user_id': [user_id]
        })
        similar_users, similarity = zip(
            *pred_df['user_id'].map(self.mapper))

        pred_fast = []
        watched_items = {}
        for similar_user, similar in zip(similar_users[0], similarity[0]):
            if similar >= 1:
                continue
            for item_id in self.watched_dict[similar_user]:
                if item_id in watched_items:
                    continue
                watched_items[item_id] = None
                rank_idf = similar * self.idf_dict[item_id]

                new = [user_id, similar_user, similar, item_id, rank_idf]
                pred_fast.append(new)

        pred_fast.sort(key=lambda x: x[-1], reverse=True)
        predictions = [x[-2] for x in pred_fast][0:10]

        return predictions

    def get_mappings(self, train):
        self.users_inv_mapping = dict(enumerate(train['user_id'].unique()))
        self.users_mapping = {v: k for k, v in self.users_inv_mapping.items()}

        self.items_inv_mapping = dict(enumerate(train['item_id'].unique()))
        self.items_mapping = {v: k for k, v in self.items_inv_mapping.items()}

    def _generate_recs_mapper(self, N: int):
        def _recs_mapper(user):
            user_id = self.users_mapping[user]
            recs = self.model.similar_items(user_id, N=N)
            maps = [self.users_inv_mapping[user] for user in recs[0]], \
                list(sim for sim in recs[1])
            maps[0].pop(0)
            maps[1].pop(0)
            return maps

        return _recs_mapper

    def prepare_watched(self):
        watched = self.dataset.groupby('user_id').agg({'item_id': list})

        watched_dict = {user_id: items["item_id"] for user_id, items
                        in watched.iterrows()}
        return watched, watched_dict

    def get_watched_dict(self):
        return self.watched_dict

    def prepare_idf(self):
        cnt = Counter(self.dataset['item_id'].values)
        idf = pd.DataFrame.from_dict(cnt, orient='index',
                                     columns=['doc_freq']).reset_index()
        # num of documents = num of recommendation list = dataframe shape
        n = self.dataset.shape[0]
        # pylint: disable = E1137, E1136
        idf['idf'] = idf['doc_freq'].apply(lambda x:
                                           np.log((1 + n) / (1 + x) + 1))

        idf_dict = {items["index"]: items["idf"] for ind, items in
                    idf.iterrows()}
        return idf, idf_dict


class Popular:
    def __init__(self, model_path):
        super().__init__()
        self.mp_items = 1500
        assert os.path.exists(model_path), "Wrong path"
        with open(model_path, 'rb') as fh:
            self.pop = dill.load(fh)

        interactions, _, items = make_dataset()
        self.dataset = self.make_dataset_year_genre(interactions, items)

        self.popular_items = list(self.pop.recommend(
            [0],
            dataset=self.dataset,
            k=self.mp_items,
            filter_viewed=False)["item_id"])

    def recommend(self, _, k: int = 10):
        reco_list = self.popular_items[:k]

        return reco_list

    def get_popular_items(self):
        return self.popular_items

    @staticmethod
    def make_dataset_year_genre(interactions: pd.DataFrame,
                                items: pd.DataFrame):
        _, bins = pd.qcut(items["release_year"], 10, retbins=True)

        items_for_years = pd.DataFrame(
            {
                "id": items["item_id"],
                "value": pd.cut(items["release_year"], bins=bins,
                                labels=bins[:-1]),
                "feature": "release_year",
            }
        )

        items["genre"] = items["genres"].str.split(",")

        items_for_genre = items[["item_id", "genre"]].explode("genre")
        items_for_genre.columns = ["id", "value"]
        items_for_genre["feature"] = "genre"

        items_year_genre = pd.concat([items_for_genre, items_for_years])
        items_year_genre = items_year_genre[items_year_genre['id'].isin(
            interactions['item_id'])]

        dataset = Dataset.construct(
            interactions_df=interactions,
            user_features_df=None,
            item_features_df=items_year_genre,
            cat_item_features=['genre', 'release_year']
        )

        return dataset


class PopularUserKnn:
    def __init__(self, user_knn_model: UserKnn, pop_model: Popular, n=10):
        super().__init__()
        self.user_knn_model = user_knn_model
        self.popular_model = pop_model
        self.n = n

    # pylint: disable=too-many-branches
    def recommend(self, user_id: int):  # noqa: C901
        try:
            reco_list = self.user_knn_model.recommend(user_id)
        except KeyError:
            # cold users fix
            reco_list = self.popular_model.get_popular_items()[:self.n]
            return reco_list

        # get up to N recos
        if len(reco_list) < self.n:
            new_reco = [*reco_list]
            watched = self.user_knn_model.get_watched_dict()[user_id]
            additional_reco = self.popular_model.get_popular_items()

            for rec in additional_reco:
                if len(new_reco) == self.n:
                    break
                if rec not in new_reco and rec not in watched:
                    new_reco.append(rec)
            if len(new_reco) < self.n:
                for rec in additional_reco:
                    if len(new_reco) == self.n:
                        break
                    if rec not in new_reco:
                        new_reco.append(rec)

            reco_list = new_reco
        if len(reco_list) != self.n:
            raise NotEnoughError(len(reco_list))

        return reco_list


class LightFMModel:
    def __init__(self, offline_lightfm_path, pop_model: Popular, n=10):
        super().__init__()
        with open(offline_lightfm_path, 'rb') as f:
            self.offline_model = pickle.load(f)

        self.popular_model = pop_model
        self.n = n

    def recommend(self, user_id: int):

        recs = self.offline_model.get(user_id)
        if recs:
            return recs
        return self.popular_model.get_popular_items()[:self.n]
