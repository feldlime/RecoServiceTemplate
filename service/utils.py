import pickle


def save_model(model_path, model) -> None:
    with open(model_path, 'wb+') as f:
        pickle.dump(model, f)


def load_model(model_path: str):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model
