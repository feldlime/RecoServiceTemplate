import pickle

import pandas as pd
from recbole.quick_start import load_data_and_model
from recbole.utils.case_study import full_sort_topk
from rectools import Columns
from rectools.dataset import Dataset


class Recommender:
    def __init__(self, dataset_path: str, warm_model_path: str, hot_model_path: str):
        # Десереализуем датасет
        self.interactions = pd.read_csv(dataset_path)
        self.interactions.rename(columns={"last_watch_dt": Columns.Datetime, "total_dur": Columns.Weight}, inplace=True)
        self.dataset = Dataset.construct(self.interactions)

        # Выбираем самое популярное
        items_ids_all = (
            self.interactions.groupby(Columns.Item)[Columns.User].nunique().reset_index(name="unique_users_count")
        )
        self.popular_items = items_ids_all.sort_values(by="unique_users_count", ascending=False).head(10)[Columns.Item]

        # Запоминаем отсутствующих юзеров
        self.missing_user_id_values = set(range(1100000)).difference(set(self.interactions[Columns.User]))

        # Сохраняем список горячих юзеров
        user_ids_all = (
            self.interactions.groupby(Columns.User)[Columns.Item].nunique().reset_index(name="unique_items_count")
        )
        self.hot_users = user_ids_all[user_ids_all["unique_items_count"] > 25][Columns.User]
        print(f"Hot users cout: {self.hot_users.shape[0]}")

        # Десереализуем холодную модель
        with open(warm_model_path, "rb") as file:
            self.warm_model = pickle.load(file)

        # Десереализуем горячую модель
        with open(hot_model_path, "rb") as file:
            (
                self.config,
                self.model,
                self.dataset,
                self.train_data,
                self.valid_data,
                self.test_data,
            ) = load_data_and_model(model_file=hot_model_path)

        print("Models loaded")

    def recommend(self, user_id: int, k_recs: int):
        # Горячий
        if self.hot_users.isin([user_id]).any():
            internal_user_list = self.dataset.token2id(self.dataset.uid_field, [str(user_id)])
            topk_score, topk_iid_list = full_sort_topk(internal_user_list, self.model, self.valid_data, k=10)
            recos = self.dataset.id2token(self.dataset.iid_field, topk_iid_list.cpu())
            return recos[0]

        # Теплый
        if user_id not in self.missing_user_id_values:
            recos = self.popular_items
            return recos

        # Холодный
        recos = self.popular_items
        return recos
