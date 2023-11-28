from rectools.dataset import Interactions, Dataset
from rectools import Columns

import pandas as pd
import pickle

class Recommender():
    def __init__(self, dataset_path: str, warm_model_path: str, hot_model_path: str):
        # Десереализуем датасет
        self.interactions = pd.read_csv(dataset_path)
        self.interactions.rename(columns={'last_watch_dt': Columns.Datetime, 'total_dur': Columns.Weight}, inplace=True)
        self.dataset = Dataset.construct(self.interactions)

        # Выбираем самое популярное
        items_ids_all = self.interactions.groupby('item_id')['user_id'].nunique().reset_index(name='unique_users_count')
        self.popular_items = items_ids_all.sort_values(by='unique_users_count', ascending=False).head(10)['item_id']

        # Запоминаем отсутствующих юзеров
        self.missing_user_id_values = set(range(1100000)).difference(set(self.interactions['user_id']))

        # Сохраняем список горячих юзеров
        user_ids_all = self.interactions.groupby('user_id')['item_id'].nunique().reset_index(name='unique_items_count')
        self.hot_users = user_ids_all[user_ids_all['unique_items_count'] > 20]['user_id']
        print(f"Hot users cout: {self.hot_users.shape[0]}")

        # Десереализуем холодную модель
        with open(warm_model_path, "rb") as file:
            self.warm_model = pickle.load(file)

        # Десереализуем горячую модель
        with open(hot_model_path, "rb") as file:
            self.hot_model = pickle.load(file)

        print("Models loaded")

        # df_hot = pd.DataFrame({'user_id': self.interactions[self.interactions['user_id'].isin(self.hot_users)]["user_id"]})
        # self.recos_hot = self.hot_model.predict(df_hot)
        #
        # print("Hot recos predicted")
        #
        # df_warm = self.interactions[~self.interactions['user_id'].isin(df_hot['user_id'])].drop_duplicates(subset='user_id')
        # self.recos_warm = self.warm_model.recommend(
        #     users=df_warm['user_id'],
        #     dataset=self.dataset,
        #     k=10,
        #     filter_viewed=True,
        # )
        #
        # print("Warm recos predicted")
        #
        # self.recos_cold = self.popular_items
        #
        # print("Cold recos predicted")

    def recommend(self, user_id: int, k_recs: int):
        # print(f"user_id {user_id} recommend body")
        # Горячий
        if self.hot_users.isin([user_id]).any():
            # return list(range(k_recs))
            # print(f"user_id {user_id} hot start predict")
            user_id_kostyl = pd.DataFrame({'user_id': [user_id]})
            recos = self.hot_model.predict(user_id_kostyl)

            # recos = self.recos_hot[ self.recos_hot['user_id'].isin([user_id])]["item_id"]
            # print(f"user_id {user_id} is hot; recos {recos}; len{len(recos)}")
            return recos["item_id"]

        # Теплый
        if user_id not in self.missing_user_id_values:
            # return list(range(k_recs))
            # print(f"user_id {user_id} warm start predict")
            # recos = self.warm_model.recommend(
            #     users=[user_id],
            #     dataset=self.dataset,
            #     k=k_recs,
            #     filter_viewed=True)
            # recos = self.recos_warm[ self.recos_warm['user_id'].isin([user_id])]["item_id"]
            # print(f"user_id {user_id} is warm; recos {recos}; len{len(recos)}")
            recos = self.popular_items
            return recos

        # Холодный
        # print(f"user_id {user_id} cold start predict")
        recos = self.popular_items
        # print(f"user_id {user_id} is cold; recos {recos}; len{len(recos)}")
        return recos

