# Copyright 2023-2023 Juan Sebastian Rojas Rodriguez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import pandas as pd

# import os
import time
import concurrent.futures
import threading
from functools import partial

import config
import utils
import shared

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def download(ticker, start, end, period='d', _filter=None,
             folderPath_rsrc='/data/'):
    """
    """
    # cwd = os.getcwd()
    # path_resources = cwd + folderPath_rsrc

    # reset shared._DFS
    shared._DFS = {}

    _BASE_URL_ = f'https://eodhd.com/api/eod/{ticker}'

    payload = {'api_token': config.api_key,
               'period': period,
               'from': start,
               'to': end,
               'fmt': 'json',
               'filter': _filter}
    session = get_session()
    r = session.get(_BASE_URL_, params=payload)
    data = r.json()
    df = pd.DataFrame(data)

    df = formatData(df)

    return df
    # # export data
    # df.to_pickle(f'{path_resources}{ticker.upper()}')
    # # df.to_excel(f'{path_results}{ticker.upper()}.xlsx')
    # # print(f"{ticker}: {r}")


def handle_data(ticker, start, end, period='d', _filter=None,
                folderPath_rsrc='/data/'):
    data = None

    try:
        data = download(ticker, start, end, period='d', _filter=None,
                        folderPath_rsrc='/data/')
    except Exception as e:
        shared._DFS[ticker.upper()] = utils.empty_df()
        shared._ERRORS[ticker.upper()] = repr(e)
    else:
        shared._DFS[ticker.upper()] = data

    return data


def downloadAllTickers(tickers, start, end, period='d', _filter=None,
                       group_by='column'):
    """
    Parameters
    ----------
    tickers: list
        Contains a list of all tickers required.
    start: int
        Start date - the format is 'YYYY-MM-DD'.
    end: int
        End date - the format is 'YYYY-MM-DD'.
    period: int
        Use 'd' for daily, 'w' for weekly, 'm' for monthly prices.
        By default, daily prices will be shown.
    _filter: int
        Use 'Open', 'High', 'Low', 'Close', 'Adjusted_close', 'Volume'.
        By default, all columns will be shown.
    group_by: str
        Group by 'ticker' or 'column' (default)

    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(partial(handle_data, start=start, end=end,
                             period=period, _filter=_filter),
                     tickers)

    data = pd.concat(shared._DFS.values(), axis=1, sort=True,
                     keys=shared._DFS.keys())

    if group_by == 'column':
        data.columns = data.columns.swaplevel(0, 1)
        data.sort_index(level=0, axis=1, inplace=True)

    return data


def formatData(df):
    """
    """
    # set index
    df.set_index('date', inplace=True)

    # adjust prices

    return df


def groupData():
    pass


if __name__ == "__main__":

    start = '2023-05-01'
    end = '2023-05-02'
    tickers = ["CHIS", "CLIX"]

    start_time = time.time()
    downloadAllTickers(tickers, start=start, end=end)
    duration = time.time() - start_time
    print(f"Elapsed time: {duration:.2f} seconds")

    # cwd = os.getcwd()
    # folderPath_rsrc = '/ETFs/Resources/'
    # path_results = cwd + folderPath_rsrc
    # # data = pd.read_pickle(f"{path_results}{tickers[0]}")

    # print()
