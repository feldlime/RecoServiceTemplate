import pandas as pd
import joblib
import yaml

from models.ann import Ann
with open('config/config_models.yml') as stream:
    config = yaml.safe_load(stream)

ANN = {
    'model_loaded': False,
    'model': None,
    'label': None,
    'distance': None,
}

UserKNN = {
    'model_loaded': False,
    'model': None,
    'reco_df': None,
}

Popular = {
    'model_loaded': False,
    'reco_df': None,
}

ALS = {
    'model_loaded': False,
    'reco_df': None,
}

SVD = {
    'model_loaded': False,
    'reco_df': None,
}

LightFM = {
    'model_loaded': False,
    'reco_df': None,
}


def load_userknn():
    global UserKNN
    if not UserKNN['model_loaded']:
        UserKNN['reco_df'] = pd.read_csv(
            config['UserKnn_model_conf']['save_reco_df_path'],
            encoding='utf-8',
        )



def load_popular():
    global Popular
    if not Popular['model_loaded']:
        Popular['reco_df'] = pd.read_csv(
            config['Popular_model_conf']['save_reco_df_path'],
            encoding='utf-8',
        )


def load_als():
    global ALS
    if not ALS['model_loaded']:
        ALS['reco_df'] = pd.read_csv(
            config['ALS_model_conf']['save_reco_df_path'],
            encoding='utf-8',
        )


def load_svd():
    global SVD
    if not SVD['model_loaded']:
        SVD['reco_df'] = pd.read_csv(
            config['SVD_model_conf']['save_reco_df_path'],
            encoding='utf-8',
        )


def load_lightfm():
    global LightFM
    if not LightFM['model_loaded']:
        LightFM['reco_df'] = pd.read_csv(
            config['LightFM_model_conf']['save_reco_df_path'],
            encoding='utf-8',
        )


def load_ann():
    global ANN
    if not ANN['model_loaded']:
        ANN['label'] = joblib.load(
            config['ANN_model_conf']['label'],
        )
        ANN['distance'] = joblib.load(
            config['ANN_model_conf']['distance'],
        )
        ANN['model'] = Ann(ANN['label'], ANN['distance'])


if __name__ == '__main__':
    load_userknn()
    load_popular()
    load_als()
    load_svd()
    load_lightfm()
    load_ann()

