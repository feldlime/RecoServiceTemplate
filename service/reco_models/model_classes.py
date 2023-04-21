from typing import Optional

import dill
import pandas as pd
import yaml

with open('service/config/config.yaml') as stream:
    config = yaml.safe_load(stream)


class UserKNN:
    model_loaded: bool = False
    model: Optional[object] = None
    recs: Optional[pd.DataFrame] = None

    @classmethod
    def load_model(cls):
        if not cls.model_loaded:
            cls.model_loaded = True
            if config['userknn_model']['online_mode']:
                with open(config['userknn_model']['online'], 'rb') as f:
                    cls.model = dill.load(f)
            else:
                cls.recs = pd.read_csv(
                    config['userknn_model']['offline'],
                    encoding='utf-8',
                )


class Popular:
    model_loaded: bool = False
    model: Optional[object] = None
    recs: Optional[pd.DataFrame] = None

    @classmethod
    def load_model(cls):
        if not cls.model_loaded:
            cls.model_loaded = True
            cls.recs = pd.read_csv(
                config['popular_model']['offline'],
                encoding='utf-8',
            )


# class LightFM:
#     model_loaded: bool = False
#     model: Optional[object] = None
#
#     @classmethod
#     def load_model(cls):
#         if not cls.model_loaded:
#             cls.model_loaded = True
#             with open(config['lightfm_model']['online'], 'rb') as f:
#                 cls.model = dill.load(f)
