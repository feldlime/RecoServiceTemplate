import os
import pickle

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'UserKnn':
            from recommenders.userknn import UserKnn
            return UserKnn
        return super().find_class(module, name)
    
def load(path:str):
        with open(os.path.join(path), 'rb') as f:
            return CustomUnpickler(f).load()