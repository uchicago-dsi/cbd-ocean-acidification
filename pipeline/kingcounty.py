import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import os
import json
from datetime import datetime
import time
import re

PATH = os.path.abspath(__file__)

def get_data(station_id=None, start_date=None, end_date=None):
    """ Retrieves data for input station(s) and time range as DataFrame.

    Args:
        station_id (str): Default None. If none supplied, retrieves data
            for all station_ids
        start_date (MM/DD/YYYY): Default None. If none supplied, 
            starts with earliest available
        end_date(MM/DD/YYYY): Default None. If none, uses current date.
    Returns:
        pd.DataFrame: Contains information on all platforms listed in the input json.
    """

    url = 'https://green2.kingcounty.gov/marine-buoy/Data.aspx'
    param_path = os.path.join(PATH, '..', '..', 'data', 'king-county', 'keys', 
        'king-county-keys.json')

    if not end_date:
        current_time = datetime.now()
        end_date = current_time.strftime('%m/%d/%Y')
    if not start_date:
        start_date = '01/01/1900'

    # Setting up the parameters for POST request
    with open(pram_path) as f:
        params = json.load(f)
    
    start_date_key = 'ctl00$kcMasterPagePlaceHolder$startDate'
    end_date_key = 'ctl00$kcMasterPagePlaceHolder$endDate'

    # Iterate over station parameters
    dfs = []
    for buoy, data in tqdm(params.items()):
        data[start_date_key] = start_date
        data[end_date_key] = end_date
        response = requests.post(url, data=data)
        tsv = response.text.split('***END***')[1]
        df = pd.read_csv(StringIO(tsv), sep='\t', low_memory=False)
        df['STATION_NAME'] = buoy
        df.dropna(how='all', axis=1, inplace=True)
        col_renames = {c: 'Measure_' + c for c in df.columns if not 
                      ((c.startswith('Qual')) | (c == 'Date') | (c == 'STATION_NAME'))}
        df.rename(columns = col_renames, inplace=True)
        dfs.append(df)

    all_measures = pd.concat(dfs, ignore_index=True)
    return(all_measures)


if __name__ == '__main__':
    df = get_data()
    data_path = os.path.join(PATH, '..', '..', 'data', 'king-county',
        'king_county_data_{}.csv'.format(str(int(time.time()))))
    df.to_csv(path, index=False)
