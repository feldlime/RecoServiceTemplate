import os

import pandas as pd

userknn_recos = pd.DataFrame()
unique_users_userknn = list()
PATH = "recos/userknn_recos.csv"
if os.path.exists(PATH):
    userknn_recos = pd.read_csv(PATH)
    unique_users_userknn = userknn_recos["user_id"].unique()

als_recos = pd.DataFrame()
unique_users_als = list()
PATH = "recos/userknn_recos.csv"
if os.path.exists(PATH):
    als_recos = pd.read_csv(PATH)
    unique_users_als = als_recos["user_id"].unique()

lightfm_recos = pd.DataFrame()
unique_users_lightfm = list()
PATH = "recos/userknn_recos.csv"
if os.path.exists(PATH):
    lightfm_recos = pd.read_csv(PATH)
    unique_users_lightfm = lightfm_recos["user_id"].unique()

popular_recos = pd.DataFrame()
PATH2 = "recos/popular.csv"
if os.path.exists(PATH2):
    popular_recos = pd.read_csv(PATH2)["item_id"].to_list()


def user_knn_model(user_id: int):
    if user_id in unique_users_userknn:
        user_recommendations = userknn_recos[userknn_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = popular_recos[:num_popular_recos]
                user_recommendations = user_recommendations + popular_recos_subset
        else:
            user_recommendations = popular_recos[:10]
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations


def als_model(user_id: int):
    if user_id in unique_users_als:
        user_recommendations = als_recos[als_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = popular_recos[:num_popular_recos]
                user_recommendations = user_recommendations + popular_recos_subset
        else:
            user_recommendations = popular_recos[:10]
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations


def lightfm_model(user_id: int):
    if user_id in unique_users_lightfm:
        user_recommendations = lightfm_recos[lightfm_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = popular_recos[:num_popular_recos]
                user_recommendations = user_recommendations + popular_recos_subset
        else:
            user_recommendations = popular_recos[:10]
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations
