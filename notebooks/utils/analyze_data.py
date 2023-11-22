import time
import copy

import numpy as np
import pandas as pd

from tqdm import tqdm
from rectools.dataset import Interactions, Dataset
from rectools import Columns
from rectools.metrics import calc_metrics
from rectools.model_selection import Splitter

from IPython.display import display


def count_metrics(
    models: dict,
    metrics: dict,
    splitter: Splitter,
    interactions: Interactions,
    k_recos: int
) -> pd.DataFrame:
    results = []

    fold_iterator = splitter.split(interactions, collect_fold_stats=True)

    for train_ids, test_ids, fold_info in tqdm(fold_iterator, total=splitter.n_splits):
        df_train = interactions.df.iloc[train_ids]
        train_set = Dataset.construct(df_train)

        df_test = interactions.df.iloc[test_ids][Columns.UserItem]
        test_users = np.unique(df_test[Columns.User])

        catalog = df_train[Columns.Item].unique()

        for model_name, model in models.items():
            model = copy.deepcopy(model)

            start = time.time()
            model.fit(train_set)
            stop = time.time()

            recos = model.recommend(
                users=test_users,
                dataset=train_set,
                k=k_recos,
                filter_viewed=True,
            )
            metric_values = calc_metrics(
                metrics,
                reco=recos,
                interactions=df_test,
                prev_interactions=df_train,
                catalog=catalog,
            )
            res = {
                "model": model_name,
                "time": stop - start
            }
            res.update(metric_values)
            results.append(res)

    results_df = pd.DataFrame(results)

    agg_mapping = dict.fromkeys(results_df.columns, ["mean", "std"])
    agg_mapping["time"] = "sum"
    agg_mapping.pop("model")

    results_df = (results_df
                  .groupby(["model"], sort=False)
                  .agg(agg_mapping))

    return results_df


def get_films_data(
    interactions_df: pd.DataFrame,
    items_data: pd.DataFrame,
    extra_columns_list: list
) -> pd.DataFrame:
    refined = items_data[['item_id'] + extra_columns_list]
    count_views = (interactions_df[['item_id', 'user_id']]
                   .groupby(['item_id'])
                   .count()
                   .rename(columns={'user_id': 'total_views'}))
    return refined.merge(count_views, on='item_id', how='left')


def get_recos_per_user(
    model,
    dataset: pd.DataFrame,
    test_users_list: list[int],
    films_data: pd.DataFrame,
    k_recos: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_set = Dataset.construct(dataset)

    recos = model.recommend(
        users=test_users_list,
        dataset=train_set,
        k=k_recos,
        filter_viewed=True
    )

    recos_extended_info = recos.merge(films_data, on='item_id', how='left')

    history = dataset[dataset['user_id'].isin(test_users_list)]
    history_extended_info = history.merge(films_data, on='item_id', how='left')

    return recos_extended_info, history_extended_info


def visual_analisys(
    usr_id: int,
    recos: pd.DataFrame,
    history: pd.DataFrame,
    users_data: pd.DataFrame
) -> None:
    users_part = users_data[users_data['user_id'] == usr_id].drop(columns=['user_id'])
    recos_part = recos[recos['user_id'] == usr_id].drop(columns=['user_id'])
    history_part = history[history['user_id'] == usr_id].drop(columns=['user_id', 'weight'])

    display('Данные о пользователе:', users_part,
            'Рекомендации:', recos_part,
            'Его история просмотра:', history_part)
