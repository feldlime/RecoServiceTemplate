import os

import pandas as pd

userknn_recos = pd.DataFrame()
unique_users_userknn = []
PATH = "service/recos/userknn_recos.csv"
if os.path.exists(PATH):
    userknn_recos = pd.read_csv(PATH)
    unique_users_userknn = userknn_recos["user_id"].unique()

als_recos = pd.DataFrame()
unique_users_als = []
PATH = "service/recos/userknn_recos.csv"
if os.path.exists(PATH):
    als_recos = pd.read_csv(PATH)
    unique_users_als = als_recos["user_id"].unique()

lightfm_recos = pd.DataFrame()
unique_users_lightfm = []
PATH = "service/recos/userknn_recos.csv"
if os.path.exists(PATH):
    lightfm_recos = pd.read_csv(PATH)
    unique_users_lightfm = lightfm_recos["user_id"].unique()

autoencoder_recos = pd.DataFrame()
unique_users_autoencoder = []
PATH = "service/recos/AERecommender_recos.csv"
if os.path.exists(PATH):
    autoencoder_recos = pd.read_csv(PATH)
    unique_users_autoencoder = autoencoder_recos["user_id"].unique()
    
recbole_recos = pd.DataFrame()
unique_users_recbole = []
PATH = "service/recos/recbole_recos.csv"
if os.path.exists(PATH):
    recbole_recos = pd.read_csv(PATH)
    unique_users_recbole = recbole_recos["user_id"].unique()

popular_recos = pd.DataFrame()
PATH2 = "service/recos/popular.csv"
if os.path.exists(PATH2):
    popular_recos = pd.read_csv(PATH2)["item_id"].to_list()


def popular_model():
    return popular_recos[:10]


def user_knn_model(user_id: int):
    if user_id in unique_users_userknn:
        user_recommendations = userknn_recos[userknn_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = [item for item in popular_recos if item not in user_recommendations]
                user_recommendations = user_recommendations + popular_recos_subset[:num_popular_recos]
        else:
            user_recommendations = popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations


def als_model(user_id: int):
    if user_id in unique_users_als:
        user_recommendations = als_recos[als_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = [item for item in popular_recos if item not in user_recommendations]
                user_recommendations = user_recommendations + popular_recos_subset[:num_popular_recos]
        else:
            user_recommendations = popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations



def lightfm_model(user_id: int):
    if user_id in unique_users_lightfm:
        user_recommendations = lightfm_recos[lightfm_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = [item for item in popular_recos if item not in user_recommendations]
                user_recommendations = user_recommendations + popular_recos_subset[:num_popular_recos]
        else:
            user_recommendations = popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations

def autoencoder_model(user_id: int):
    if user_id in unique_users_autoencoder:
        user_recommendations = autoencoder_recos[autoencoder_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = [item for item in popular_recos if item not in user_recommendations]
                user_recommendations = user_recommendations + popular_recos_subset[:num_popular_recos]
        else:
            user_recommendations = popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations

def recbole_model(user_id: int):
    if user_id in unique_users_recbole:
        user_recommendations = recbole_recos[recbole_recos["user_id"] == user_id]["item_id"].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                user_recommendations = user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = [item for item in popular_recos if item not in user_recommendations]
                user_recommendations = user_recommendations + popular_recos_subset[:num_popular_recos]
        else:
            user_recommendations = popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        user_recommendations = popular_recos[:10]
    return user_recommendations