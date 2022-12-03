from recommendations.discover import discover_models


def load_model(model_name, *args, **kwargs):
    models = discover_models()
    if model_name not in models:
        raise ValueError(f"Unknown model `{model_name}`")
    return models[model_name](*args, **kwargs)
