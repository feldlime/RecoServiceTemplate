import os
import warnings
import zipfile

import pandas as pd
import requests
from rectools import Columns
from tqdm import tqdm

warnings.filterwarnings("ignore")


def download_dataset():
    # download dataset by chunks
    url = 'https://github.com/irsafilo/KION_DATASET/raw/f69775be31fa5779907cf0a92ddedb70037fb5ae/data_original.zip'

    timeout = 1000
    req = requests.get(url, stream=True, timeout=timeout)

    with open('kion.zip', 'wb') as fd:
        total_size_in_bytes = int(req.headers.get('Content-Length', 0))
        progress_bar = tqdm(desc='kion dataset download',
                            total=total_size_in_bytes, unit='iB',
                            unit_scale=True)
        for chunk in req.iter_content(chunk_size=2 ** 20):
            progress_bar.update(len(chunk))
            fd.write(chunk)


def read_dataset():
    users = pd.read_csv('service/models/data_original/users.csv')
    items = pd.read_csv('service/models/data_original/items.csv')

    interactions = pd.read_csv('service/models/data_original/interactions.csv',
                               parse_dates=["last_watch_dt"])
    # rename columns
    interactions.rename(
        columns={
            'last_watch_dt': Columns.Datetime,
            'total_dur': Columns.Weight
        },
        inplace=True)

    return interactions, users, items


# pylint: disable=too-many-boolean-expressions
def make_dataset():
    if not os.path.exists("kion.zip"):
        download_dataset()
    if not os.path.exists("service/models/data_original/interactions.csv") or \
        not os.path.exists("service/models/data_original/users.csv") or \
        not os.path.exists("service/models/data_original/items.csv"
                           ):
        with zipfile.ZipFile("kion.zip", 'r') as zip_ref:
            zip_ref.extractall('service/models')

    interactions, users, items = read_dataset()

    return interactions, users, items


if __name__ == '__main__':
    make_dataset()
