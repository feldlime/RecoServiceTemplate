import random
import pandas as pd


top_20 = pd.read_csv("data/top_20_items.csv")
top_weight_duration = pd.read_csv("data/top_weight_items.csv")
top_items = pd.read_csv("data/top_items.csv")
viewed_films = pd.read_csv("data/viewed_films.csv")

top_items_list = top_items.sort_values('views', ascending=False)[
    "item_id"].to_list()


def top_popular(k=10):
    reco = top_20["item_id"].head(k).to_list()
    return reco


def weighted_random_recommendation(n, items_weights=top_weight_duration):
    reco = random.choices(items_weights['item_id'], items_weights['weight'],
                          k=n)
    return reco


def top_popular_without_viewed(user_id, k=10):
    top = top_items_list
    if len(viewed_films[viewed_films["user_id"] == user_id][
               "items_list_id"].to_list()) > 0:
        viewed_films_user = \
            viewed_films[viewed_films["user_id"] == user_id][
                "items_list_id"].to_list()[
                0]
    else:
        viewed_films_user = []

    for i in range(len(viewed_films_user)):
        if viewed_films_user[i] in top:
            top.remove(viewed_films_user[i])

    reco = top_items_list[:k]
    return reco
