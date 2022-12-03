import numpy as np


class ZeroModel:
    name = "zero"

    def fit(self, df):
        return self

    def recommend(self, user_ids=None, k=10):
        return np.array(range(k))
