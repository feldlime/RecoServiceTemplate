import os

from recommenders.model_loader import load
from recommenders.popular import get_popular


def test_popular():
    k_recs = 10
    reco = get_popular(k_recs)
    assert isinstance(reco, list)
    assert len(reco) == k_recs


def test_userknn():
    MODEL_PATH = "models/user_knn.pkl"
    if os.path.exists(MODEL_PATH):
        userknn_model = load("models/user_knn.pkl")
        user_id = 0
        k_recs = 10
        reco = userknn_model.recommend(user_id, N_recs=k_recs)
        assert isinstance(reco, list)
        assert len(reco) == k_recs
    else:
        pass
