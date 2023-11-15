from collections import Counter

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from service.api.exceptions import UserNotFoundError

# users = pd.read_csv("service/api/recsys/kion_train/users.csv")
# interactions = pd.read_csv("service/api/recsys/kion_train/interactions.csv")


def user_based_recsys(user_id, n_recommendations=10):
    if user_id not in users["user_id"].values:
        return []
    user_info = users[users["user_id"] == user_id]
    user_sex = user_info["sex"].iloc[0]
    user_age = user_info["age"].iloc[0]

    user_items = set(interactions[interactions["user_id"] == user_id]["item_id"])

    filtered_users = set(users[(users["sex"] == user_sex) & (users["age"] == user_age)]["user_id"])
    active_interactions = interactions[
        (
            (interactions["watched_pct"] > 90)
            & (interactions["item_id"].isin(user_items))
            & (interactions["user_id"].isin(filtered_users))
        )
        | (interactions["user_id"] == user_id)
    ]

    if active_interactions.shape[0] == 0:
        return []

    if active_interactions.shape[0] > 1000:
        active_interactions = active_interactions.sample(n=1000)

    user_item_matrix = active_interactions.pivot_table(
        index="user_id", columns="item_id", values="watched_pct", fill_value=0
    )

    similarity_matrix = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)

    similar_users = similarity_df[user_id].nlargest(n_recommendations + 1).index[1:]

    item_counts = Counter()
    for similar_user in similar_users:
        similar_user_items = set(interactions[interactions["user_id"] == similar_user]["item_id"])
        new_recommendations = similar_user_items.difference(user_items)
        item_counts.update(new_recommendations)

    top_recommendations = [item for item, _ in item_counts.most_common(n_recommendations)]

    return top_recommendations


def find_top_movies(n=10):
    high_watch_pct_interactions = interactions[interactions["watched_pct"] > 95]
    total_watch_time_per_movie = high_watch_pct_interactions.groupby("item_id")["total_dur"].sum()
    top_movies = total_watch_time_per_movie.nlargest(n).index.tolist()
    return top_movies


def complete_array_to_ten(recommendations, top_movies):
    elements_to_add = 10 - len(recommendations)
    if elements_to_add > 0:
        recommendations.extend(top_movies[:elements_to_add])

    return recommendations


def get_reccomendation(user_id, n_recommendations=10):
    rec = user_based_recsys(user_id)
    if len(rec) == 10:
        return rec
    popular = find_top_movies(n=10)
    rec = complete_array_to_ten(rec, popular)
    return rec
