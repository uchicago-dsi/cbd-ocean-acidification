import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import time
import os

ASSET_LIST_URL = 'http://www.ipacoa.org/services/download_asset_list.php'
IPACOA_URL = 'http://www.ipacoa.org/ssa/get_recent_measurements.php'

class NoDataError(Exception):
    pass

def get_asset_list(url=ASSET_LIST_URL):
    response = requests.get(url)
    
    # Raise error if request is not successful
    response.raise_for_status()
    
    asset_list = pd.read_csv(StringIO(response.text))
    return asset_list

def get_station_data(station_id, url=IPACOA_URL):
    params = (('platform_label', station_id),)
    response = requests.get(url, params)

    # Raise error if request is not successful
    response.raise_for_status()
    
    raw_data = response.json()
    
    # Check whether any data 
    if not raw_data['success']:
        raise NoDataError('There was no data returned by IPACOA, '
        	'make sure parameters are valid.')
    
    df = pd.DataFrame(raw_data['result'])
    return df

def scrape_ipacoa():
    asset_list = get_asset_list()
    station_ids = asset_list['ID']
    dfs = []
    for sid in tqdm(station_ids):
        station_df = get_station_data(sid)
        dfs.append(station_df)
    df_all = pd.concat(dfs)
    return df_all

if __name__ == "__main__":
	df_all = scrape_ipacoa()
	path = os.path.join('..', 'data', 'ipacoa_data_' + str(int(time.time())) + '.csv')
	df_all.to_csv(path, index=False)


