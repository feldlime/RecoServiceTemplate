import annoy
import hnswlib
import nmslib
import pandas as pd

import numpy as np

from typing import Literal

from rectools import Columns
from rectools.dataset import Dataset
from rectools.models import ImplicitALSWrapperModel, LightFMWrapperModel


class HNSWrapper():
    def __init__(self, dim_size: int, n_neighbours: int = 10, **params_dict: dict) -> None:
        self.M = params_dict['M']
        self.efc = params_dict['efConstruction']
        self.n_neighbours = n_neighbours
        self.hnsw = hnswlib.Index(params_dict['space_type'], dim_size)

    def fit(self, vectors: np.ndarray) -> None:
        self.hnsw.init_index(len(vectors), self.M, self.efc)
        self.hnsw.add_items(vectors)
        self.hnsw.set_ef(self.efc)

    def predict(self, vector: np.ndarray) -> list:
        label, distance = self.hnsw.knn_query(vector, k=self.n_neighbours, num_threads=8)
        return list(label[0])


class AnnoyWrapper():
    def __init__(self, dim_size: int, n_neighbours: int = 10, **params_dict: dict) -> None:
        metric = params_dict['metric']
        self.n_trees = params_dict['n_trees']

        self.index = annoy.AnnoyIndex(dim_size, metric)
        self.n_neighbours = n_neighbours

    def fit(self, vectors: np.ndarray) -> None:
        for i in range(len(vectors)):
            self.index.add_item(i, vectors[i])
        self.index.build(self.n_trees)

    def predict(self, vector: np.ndarray) -> list:
        return (self.index.get_nns_by_vector(vector[0], self.n_neighbours))


class NMSLIBWrapper():
    def __init__(self, dim_size: int, n_neighbours: int = 10, **params_dict: dict) -> None:
        self.n_neighbours = n_neighbours
        self.params_dict = params_dict
        self.params_dict.update({'indexThreadQty':8})
        self.index = nmslib.init(method='hnsw', space='negdotprod', data_type=nmslib.DataType.DENSE_VECTOR)  

    def fit(self, vectors: np.ndarray):
        self.index.addDataPointBatch(vectors)
        self.index.createIndex(self.params_dict, print_progress=False)      

    def predict(self, vector: np.ndarray) -> list:
        ids, distances = self.index.knnQuery(vector, k=self.n_neighbours)
        return list(ids)


class AnnRecommender():
    def __init__(self,
                 ann_class: NMSLIBWrapper | AnnoyWrapper | HNSWrapper,
                 ann_params: dict,
                 embedder: ImplicitALSWrapperModel | LightFMWrapperModel,
                 n_recos: int = 10):
        self.embedder = embedder
        self.n_recos = n_recos
        self.ann_class = ann_class
        self.ann_params = ann_params

        self.fitted = False

    def fit(self, dataset: Dataset) -> None:
        self.embedder.fit(dataset)

        self.user_id_map = dataset.user_id_map
        self.item_id_map = dataset.item_id_map

        if isinstance(self.embedder, ImplicitALSWrapperModel): 
            user_embeddings, item_embeddings = self.embedder.get_vectors()
        else:
            user_embeddings, item_embeddings = self.embedder.get_vectors(dataset)

        self.user_embeddings = self._transform_embeddings_(embeddings=user_embeddings,
                                                           embedd_type='users')
        self.item_embeddings = self._transform_embeddings_(embeddings=item_embeddings,
                                                           embedd_type='items')

        self.top_n_items = (dataset.interactions.df
                            .groupby([Columns.Item])[Columns.Item]
                            .count()
                            .sort_values(ascending=False)[:self.n_recos]
                            .index
                            .to_list())

        self.ann_model = self.ann_class(self.item_embeddings.shape[1],
                                        n_neighbours=self.n_recos,
                                        **self.ann_params)
        self.ann_model.fit(self.item_embeddings)

        self.fitted = True

    def recommend_single(self, id: int, n_recos: int | None = None) -> np.ndarray:
        if n_recos is None:
            n_recos = self.n_recos

        if id not in self.user_id_map.external_ids:
            recos = self.top_n_items
        else:
            id = self.user_id_map.convert_to_internal([id])
            user_embedding = self.user_embeddings[id]
            recos = self.ann_model.predict(user_embedding)
            recos = self.item_id_map.convert_to_external(recos)

        return recos

    def recommend(self, ids_list: list[int]) -> pd.DataFrame:
        recos_list = []
        ranks_list = [np.arange(1, self.n_recos + 1)] * len(ids_list)

        for idx in ids_list:
            recos_list.append(self.recommend_single(idx))

        df = pd.DataFrame({
            Columns.User: ids_list,
            Columns.Item: recos_list,
            Columns.Rank: ranks_list
        })

        df = df.explode(column=[Columns.Item, Columns.Rank], ignore_index=True)  # костыль, что бы работал calc_metrics
        df = df.astype({Columns.User: 'int', Columns.Item: 'int', Columns.Rank: 'float'})

        return df

    def _transform_embeddings_(self, embeddings: np.ndarray, embedd_type: Literal['items', 'users']) -> np.ndarray:
        if embedd_type == 'items':
            normed_embeddings = np.linalg.norm(embeddings, axis=1)
            max_norm = normed_embeddings.max()
            extra_dim = np.sqrt(max_norm ** 2 - normed_embeddings ** 2).reshape(-1, 1)
        else:
            extra_dim = np.zeros((embeddings.shape[0], 1))

        augmented_factors = np.append(embeddings, extra_dim, axis=1)
        return augmented_factors
