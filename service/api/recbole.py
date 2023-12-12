# Load model and optimizer state dictionaries
from collections import Counter
from typing import Dict
import torch
import numpy as np
import pandas as pd
import scipy as sp
from implicit.nearest_neighbours import ItemItemRecommender
from annoy import AnnoyIndex

checkpoint = torch.load('recbole.pth')
model.load_state_dict(checkpoint['state_dict'])

import numpy as np

class RecBoleRecommender:
    def __init__(self, dataset):
        self.dataset = dataset

    def recommend_items_to_user(self, external_user_id):
        if (
            external_user_id in self.dataset.field2token_id[self.dataset.uid_field]
            and external_user_id != "[PAD]"
        ):
            # Map external user ID to internal user index
            internal_user_index = self.dataset.field2token_id[self.dataset.uid_field][external_user_id]

            # Extract user metadata features and interaction vector
            user_metadata_features = self.dataset.users_ohe_df.drop(["user_id"], axis=1).iloc[internal_user_index]
            user_interaction_vector = self.dataset.interactions_vec[internal_user_index]

            # Predict user vector using the trained user-to-vector model
            user_vector = self.dataset.u2v.predict(
                [np.array(user_metadata_features).reshape(1, -1), np.array(user_interaction_vector).reshape(1, -1)],
                verbose=False,
            )

            # Instead of calculating distance for all items, just select a random subset
            sampled_item_indices = np.random.choice(self.dataset.item_embeddings.shape[0], size=100, replace=False)
            sampled_item_embeddings = self.dataset.item_embeddings[sampled_item_indices, :]

            # Calculate distances between the user vector and sampled item embeddings
            distances = np.linalg.norm(user_vector - sampled_item_embeddings, axis=1)

            # Get the indices of the top 10 items from the sampled set
            topn_item_indices_sampled = np.argsort(distances)[:10]

            # Map internal item indices to item_ids
            topn_item_ids = [self.dataset.iid_to_item_id[iid] for iid in topn_item_indices_sampled]

            return topn_item_ids

        return []

# Example of usage:
# recommender = RecBoleRecommender(your_dataset_instance)
# recommended_items = recommender.recommend_items_to_user(your_external_user_id)
# print(f"Recommended items: {recommended_items}")
