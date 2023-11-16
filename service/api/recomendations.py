import os

import pandas as pd

DATASET_DIR = "kion_train"
popularity_df = pd.read_csv(os.path.join(DATASET_DIR, "popular_50.csv"))


def get_popular(k_recs: int = 10):
    popular = popularity_df.head(k_recs).item_id.tolist()
    return popular
