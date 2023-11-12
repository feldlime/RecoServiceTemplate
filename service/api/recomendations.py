import os

import pandas as pd

DATASET_DIR = "kion_train"
interactions_df = pd.read_csv(os.path.join(DATASET_DIR, "interactions.csv"), parse_dates=["last_watch_dt"])


def get_popular(k_recs: int = 10):
    popularity = (
        interactions_df.groupby("item_id")
        .agg({"user_id": "count", "total_dur": "sum"})
        .rename(columns={"user_id": "views"})
    )
    popularity.sort_values(["views", "total_dur"], ascending=False, inplace=True)
    popular = popularity.head(k_recs).index.tolist()
    return popular
