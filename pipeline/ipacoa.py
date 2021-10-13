import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import time
import os

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
        pd.DataFrame: Contains information on all platforms listed in the input csv.
    """

    url = 'http://www.ipacoa.org/ssa/get_platform_data.php'
    measurements_path = os.path.join(PATH, '..', '..', 'data', 'ipacoa', 'lookups', 
        'platform_measurements.csv')

    # Setting up parameters for GET request
    platform_measurement = pd.read_csv(path)
    if station_id:
        mask = platform_measurement['platform_label'] == station_id
        platform_measurement = platform_measurement[mask]
    
    # Iterate over platform * measurement combinations
    dfs = []
    for i, (platform, measurement) in tqdm(platform_measurement.iterrows(), 
                                           total=platform_measurement.shape[0]):
        params = (
            ('platform_id', platform),
            ('var_id', measurement),
            ('data_type', 'csv'),
        )
        response = requests.get(url, params=params)
        
        # Raise error if request is not successful
        response.raise_for_status()

        if response.text == '': 
            continue
        df = pd.read_csv(StringIO(response.text))
        df['platform_id'] = platform
        df['value'] = df.pop(df.columns[2])
        df['measurement_id'] = measurement
        df.rename(columns={' Depth (Ft)': 'depth_ft',
                          'Date and Time': 'date_time'},
                 inplace=True)
        df['depth_ft'] = df['depth_ft'].str.strip(' ft').astype(int)
        df = df[['date_time', 'platform_id', 'measurement_id', 'depth_ft', 'value']]
        dfs.append(df)

    all_measures = pd.concat(dfs, ignore_index=True)
    if start_date:
        start_date = pd.to_datetime(start_date)
        all_measures = all_measures[all_measures['date_time'] >= start_date]
    if end_date:
        end_date = pd.to_datetime(end_date)
        all_measures = all_measures[all_measures['date_time'] <= end_date]
    return all_measures

if __name__ == "__main__":
    df_all = get_data()
    data_path = os.path.join(PATH, '..', '..', 'data', 'ipacoa',
        'ipacoa_data_{}.csv'.format(str(int(time.time()))))
    df_all.to_csv(path, index=False)