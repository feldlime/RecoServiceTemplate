from models import model_zero

ModelsList = {
    "model_0": model_zero.Model
}

__all__ = ["load_model"]


def load_model(model_name, *args, **kwargs):
    model = ModelsList[model_name](model_name, *args, **kwargs)
    return model
