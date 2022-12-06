import numpy as np
import pandas as pd
from rectools import Columns


class UsersKFoldPOut:
    def __init__(self, n_folds, p, random_seed=23):
        self.n_folds = n_folds
        self.p = p
        self.random_seed = random_seed

    def split(self, df):
        df = df.sort_values(
            by=[Columns.Datetime], ascending=False)
        df["order"] = df.groupby(Columns.User).cumcount() + 1

        users = df[df["order"] >= self.p]["user_id"].unique()
        users_count = len(users)

        np.random.seed(self.random_seed)
        np.random.shuffle(users)

        fold_sizes = np.full(self.n_folds, users_count // self.n_folds,
                             dtype=int)
        fold_sizes[: users_count % self.n_folds] += 1
        current = 0
        for fold_size in fold_sizes:
            start, stop = current, current + fold_size
            test_fold_users = users[start:stop]
            test_mask = df["user_id"].isin(test_fold_users)
            train_mask = ~test_mask

            yield train_mask, test_mask
