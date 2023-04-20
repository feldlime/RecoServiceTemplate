git # Popular models and its data
POPULAR_MODEL_RECS = "models/popular_dictionary.pickle"
POPULAR_MODEL_USERS = "models/users_dictionary.pickle"
POPULAR_IN_CATEGORY = "models/popular_in_category/popular_in_category_model.dill"

# KNN models and its data
OFFLINE_KNN_MODEL_PATH = "models/offline-dictionary-with-hot-knn-recs.dill"
ONLINE_KNN_MODEL_PATH = "models/user-knn.dill"

# Factorization Machines models and its data
LIGHT_FM = "models/light_fm.dill"
USER_MAPPING = "models/user_mapping.dill"
ITEM_MAPPING = "models/item_mapping.dill"
FEATURES_FOR_COLD = "models/features_for_cold.dill"
UNIQUE_FEATURES = "models/unique_features.dill"

ANN_user_m = "models/lightfm/user_mapping.dill"
ANN_item_inv_m = "models/lightfm/item_inv_mapping.dill"
ANN_index_path = "models/lightfm/items_index.hnsw"
ANN_user_emb = "models/lightfm/user_embeddings.dill"
ANN_watched_u2i = "models/lightfm/watched_user2items_dictionary.dill"
ANN_COLD_RECO_DICT = "models/lightfm/lightfm_cold_users_reco_dictionary_popular.dill"

ANN_PATHS = (
    ANN_user_m,
    ANN_item_inv_m,
    ANN_index_path,
    ANN_user_emb,
    ANN_watched_u2i,
    ANN_COLD_RECO_DICT,
)
