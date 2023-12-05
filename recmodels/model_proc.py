import os
import pickle
import pandas as pd

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'UserKnn':
            from recmodels.userknn import UserKnn
            return UserKnn
        return super().find_class(module, name)

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'UserKnn':
            return UserKnn
        return super().find_class(module, name)

def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    with open(path, 'rb') as f:
        try:
            return CustomUnpickler(f).load()
        except Exception as e:
            raise RuntimeError(f"Failed to load the model from '{path}': {e}")
