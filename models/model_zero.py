
# TODO make a base class for all models; Need more data to do that
class Model:
    """
    This is not even a model :D
    """
    def __init__(self, name, *args, **kwargs):
        self._name = name

    @property
    def name(self):
        return self._name

    def predict(self, k_recs: int):
        return list(range(k_recs))
