import numpy as np
from tqdm import tqdm

class  Recommend_items_to_user(user_id, item_embeddings, topn=10, sample_size=100):
    # Map user_id to internal user index
    internal_user_index = user_id_to_uid[user_id]

    # Introduce randomness in user selection
    random_user_index = np.random.choice(list(users_ohe_df.index))

    # Extract user metadata features and interaction vector
    user_metadata_features = users_ohe_df.drop(["user_id"], axis=1).iloc[random_user_index]
    user_interaction_vector = interactions_vec[random_user_index]

    # Predict user vector using the trained user-to-vector model
    user_vector = u2v.predict(
        [np.array(user_metadata_features).reshape(1, -1), np.array(user_interaction_vector).reshape(1, -1)],
        verbose=False,
    )

    # Instead of calculating distance for all items, just select a random subset
    sampled_item_indices = np.random.choice(item_embeddings.shape[0], size=sample_size, replace=False)
    sampled_item_embeddings = item_embeddings[sampled_item_indices, :]

    # Calculate distances between the user vector and sampled item embeddings
    distances = ED(user_vector, sampled_item_embeddings)

    # Get the indices of the topn items from the sampled set
    topn_item_indices_sampled = np.argsort(distances, axis=1)[:, :topn]

    # Map internal item indices to item_ids
    topn_item_ids = [iid_to_item_id[iid] for iid in topn_item_indices_sampled.reshape(-1)]

    return topn_item_ids

