from service.api.recomendations import get_popular


def test_popular():
    k_recs = 10
    reco = get_popular(k_recs)
    assert isinstance(reco, list)
    assert len(reco) == k_recs
