import pandas as pd
import joblib
import yaml

from rectools import Columns
from rectools.model_selection import TimeRangeSplit
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


interactions = None
train = None


def cv_generate():
    global interactions
    n_folds = config['UserKnn_model_conf']['n_folds']
    unit = config['UserKnn_model_conf']['unit']
    n_units = config['UserKnn_model_conf']['n_units']
    periods = config['UserKnn_model_conf']['periods']
    freq = f"{n_units}{unit}"
    last_date = interactions[Columns.Datetime].max().normalize()
    start_date = last_date - pd.Timedelta(n_folds * n_units + 1, unit=unit)
    date_range = pd.date_range(start=start_date, periods=periods, freq=freq,
                               tz=last_date.tz)
    # folds
    cv = TimeRangeSplit(
        date_range=date_range,
        filter_already_seen=True,
        filter_cold_items=True,
        filter_cold_users=True,
    )
    return cv.split(interactions, collect_fold_stats=True).__next__()


def load_data():
    global train
    global interactions
    interactions = pd.read_csv(
        '{0}/interactions.csv'.format(
            config['UserKnn_model_conf']['dataset_path']
        )
    )

    interactions.rename(columns={'last_watch_dt': Columns.Datetime,
                                 'total_dur': Columns.Weight},
                        inplace=True)
    interactions['datetime'] = pd.to_datetime(interactions['datetime'])
    (train_ids, test_ids, fold_info) = cv_generate()
    train = interactions.loc[train_ids]


def load_userknn():
    global USERKNN
    if not USERKNN['model_loaded']:
        USERKNN['model_loaded'] = True
        if config['UserKnn_model_conf']['online']:
            with open(config['UserKnn_model_conf']['weight_path'], 'rb') as f:
                USERKNN['model'] = dill.load(f)
        else:
            USERKNN['reco_df'] = pd.read_csv(
                config['UserKnn_model_conf']['save_reco_df_path'],
                encoding='utf-8',
            )


def load_popular():
    global POPULAR
    if not POPULAR['model_loaded']:
        POPULAR['reco_df'] = pd.read_csv(
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
    global LIGHTFM
    if not LIGHTFM['model_loaded']:
        LIGHTFM['reco_df'] = pd.read_csv(
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


def main():
    global interactions
    global train
    load_data()
    load_userknn()
    load_popular()
    load_als()
    load_svd()
    load_lightfm()
    load_ann()
    interactions = train















