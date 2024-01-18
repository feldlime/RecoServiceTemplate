from service.models.models_classes import LightFMModel, Popular, RangeTest


class RecommendationValidator:
    def __init__(self):
        self.popular_model = Popular(
            'service/models/weights/popular.dill')

        self.lightfm = LightFMModel(
            'service/models/weights/offline_lightfm.pkl',
            self.popular_model)
        self.range_test = RangeTest()

        self.model_names = {
            "range_test": self.range_test,
            "popular": self.popular_model,
            'lightfm': self.lightfm
        }

    def get_model(self, model_name: str):
        if model_name not in self.model_names:
            return None
        return self.model_names[model_name]
