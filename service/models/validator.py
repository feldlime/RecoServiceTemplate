from service.models.models_classes import Popular, PopularUserKnn, RangeTest, UserKnn


class RecommendationValidator:
    def __init__(self):
        self.popular_model = Popular(
            'service/models/weights/popular.dill')
        #
        self.user_model = UserKnn(
            r"service/models//weights/userknn.dill")
        self.popular_knn = PopularUserKnn(self.user_model, self.popular_model)
        self.range_test = RangeTest()
        self.model_names = {
            "range_test": self.range_test,
            "popular": self.popular_model,
            "userknn_base": self.user_model,
            "popular_knn": self.popular_knn
        }

    def get_model(self, model_name: str):
        if model_name not in self.model_names.keys():
            return None
        else:
            return self.model_names[model_name]
