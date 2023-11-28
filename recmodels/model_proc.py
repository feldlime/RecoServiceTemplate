import os
import pickle
import pandas as pd
from recmodels.userknn import UserKnn

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

def predict(userknn_model: UserKnn, user_id: int, N_recs: int = 10):
  
    user_df = pd.DataFrame([user_id], columns=['user_id'])
    recommendations = userknn_model.predict(user_df, N_recs=N_recs)
  
    return recommendations
