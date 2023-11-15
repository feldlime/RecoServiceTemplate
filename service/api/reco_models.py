from abc import ABC, abstractmethod


class BaseModel(ABC):
    @abstractmethod
    def get_reco(self):
        pass


class DummyModel(BaseModel):
    def get_reco(self, user_id, k_recs):
        return list(range(k_recs))


models_dict = {
    'dummy_model': DummyModel()
}
