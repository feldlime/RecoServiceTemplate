import numpy as np

class Recommender:
    def __init__(self, items_ohe_df):
        self.items_ohe_df = items_ohe_df

    def recommend_items_to_user(self, user_vec, items_vecs, top_n=10):
        # Calculate Euclidean distances
        dists = np.linalg.norm(user_vec - items_vecs, axis=1)

        # Get indices of top N items with smallest distances
        top_indices = np.argsort(dists)[:top_n]

        # Get corresponding item IDs
        recommended_item_ids = self.items_ohe_df.iloc[top_indices]['item_id'].tolist()

        return recommended_item_ids

    def recommend(self, external_user_id, model, dataset):
        # Obtain user vector and items vectors
        user_vec = self.get_user_vector(external_user_id, model, dataset)
        items_vecs = self.get_items_vectors()  # You need to implement get_items_vectors

        # Make recommendations
        recommended_items = self.recommend_items_to_user(user_vec, items_vecs)
        return recommended_items


