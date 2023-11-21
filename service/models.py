import typing as tp

from pydantic import BaseModel

from rectools import Columns
from rectools.dataset import Dataset
from rectools.models import PopularModel

import pandas as pd


class TopKPopular:
    def __init__(self) -> None:
        self.name = 'top_popular'
        self.model = PopularModel()
        self.dataset = self._init_dataset()
        self.recomendations = None
    
    def recomend(self):
        if self.recomendations is None:
            self._fit_recomend()
        return self.recomendations

    def _init_dataset(self):
        interactions = pd.read_csv('./data/interactions.csv')[['user_id', 'item_id', 'last_watch_dt', 'total_dur']]
        interactions.columns = [Columns.User, Columns.Item, Columns.Datetime, Columns.Weight]
        dataset = Dataset.construct(interactions)
        return dataset

    def _fit_recomend(self):
        self.model.fit(self.dataset)
        recs = self.model.recommend(
                users=[602509],
                dataset=self.dataset,
                k=10,
                filter_viewed=False
            )
        self.recomendations = list(recs['item_id'].values)


class Error(BaseModel):
    error_key: str
    error_message: str
    error_loc: tp.Optional[tp.Any] = None
