from datetime import datetime

import numba as nb
import numpy as np
import pandas as pd
from rectools import Columns


def plook(ind, rels):
    if ind == 0:
        return 1
    return plook(ind - 1, rels) * (1 - rels[ind - 1]) * (1 - 0.15)


def pfound(group):
    # максимальный рейтинг хоста
    max_by_host = group.groupby("hostid")["rating"].max()
    # берем топ10 урлов с наивысшим рейтингом
    top10 = max_by_host.sort_values(ascending=False).iloc[:10]
    pfound = 0
    for ind, val in enumerate(top10):
        pfound += val * plook(ind, top10.values)
    return pfound


def pfound_fast(group):
    max_by_host = group.groupby("hostid")["rating"].max().to_numpy()
    top10 = np.flip(np.sort(max_by_host))[:10]

    plook_vals = (np.ones(10) - top10) * (1 - 0.15)
    plook_vals = np.append(np.ones(1), plook_vals).cumprod()[:10]

    return np.dot(plook_vals, top10)


def mrr_naive(users, target, recs):
    mrr = [0 for _ in users]
    for i, user in enumerate(users):
        rr = 0
        user_target = target[target[:, 0] == user][:, 1]
        for rank, rec in enumerate(recs[i]):
            if rec in user_target:
                rr = rank + 1
                break
        if rr != 0:
            mrr[i] = 1 / rr
    return sum(mrr) / len(mrr)


@nb.njit(cache=True, parallel=True)
def mrr_numba(users, target, recs):
    rr = np.zeros(len(users))
    for i in nb.prange(len(rr)):
        user = users[i]
        p = 0
        user_target = target[target[:, 0] == user][:, 1]
        for ind, rec in enumerate(recs[i]):
            if rec in user_target:
                p = 1 / (ind + 1)
                break
        rr[i] = p
    return sum(rr) / len(rr)


def mrr_pandas(users, df, recs):
    k = recs.shape[1]
    df_recs = pd.DataFrame({
        Columns.User: np.repeat(users, k),
        Columns.Item: recs.ravel()
    })
    df_recs[Columns.Rank] = df_recs.groupby(Columns.User).cumcount() + 1
    df_recs = df.merge(df_recs, how='inner', left_on=Columns.UserItem,
                       right_on=Columns.UserItem)
    min_by_user = df_recs.groupby(Columns.User)[Columns.Rank].min()
    return np.sum(1.0 / min_by_user) / len(users)
