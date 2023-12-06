import os
import pandas as pd

userknn_recos = pd.DataFrame()
unique_users_userknn = list()
PATH = "recos/userknn_recos.csv"
if os.path.exists(PATH):
    userknn_recos = pd.read_csv(PATH)
    unique_users_userknn = userknn_recos['user_id'].unique()

popular_recos = pd.DataFrame()
PATH2 = "recos/popular.csv"
if os.path.exists(PATH2):
    popular_recos = pd.read_csv(PATH2)['item_id'].to_list()

def user_knn_model(user_id):
    if user_id in unique_users_userknn:
        user_recommendations = userknn_recos[userknn_recos['user_id'] == user_id]['item_id'].to_list()
        if user_recommendations:
            if len(user_recommendations) >= 10:
                return user_recommendations[:10]  # Вернуть первые 10 рекомендаций
            else:
                num_popular_recos = 10 - len(user_recommendations)
                popular_recos_subset = popular_recos[:num_popular_recos]
                return user_recommendations + popular_recos_subset + [0] * num_popular_recos
        else:
            return popular_recos[:10]  # Вернуть первые 10 популярных рекомендаций
    else:
        return popular_recos[:10]
    