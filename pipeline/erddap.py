from datetime import datetime, timedelta
from urllib.error import HTTPError
import pandas as pd
import numpy as np
from erddapy import ERDDAP
import requests

COL_RENAMES = {
    'time (UTC)': 'datetime',
    'latitude (degrees_north)': 'latitude',
    'longitude (degrees_east)': 'longitude',
    'sea_water_practical_salinity': 'salinity',
    'station': 'staion_id',
    'sea_water_ph_reported_on_total_scale': 'pH',
    'sea_water_temperature' : 'water_temperature',
    'mass_concentration_of_oxygen_in_sea_water' : 'oxygen_concentration',
    'fractional_saturation_of_oxygen_in_sea_water' : 'oxygen_saturation',
    'sea_water_electrical_conductivity' : 'conductivity',
    'total_dissolved_solids' : 'total_dissolved_solids',
    'sea_water_turbidity' : 'turbidity',
    'total_alkalinity_ta' : 'total_alkalinity',
    'z (m)': 'z'
}

def get_location_data(
        server_id,
        start_time,
        end_time
):
    """ Generates dataframe of west coast pH datasets from server_id 
    
    Args:
        server_id (str): URL of ERDDAP server
        start_time (datetime): start of time window of interest
        end_time (datetime): end of time window of interest
    Returns:
        (pd.DataFrame): Each row is dataset hosted by server that
        measures pH and is generally located on the US west coast.
    """
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    # Approximate box containing all water within 3 miles of west coast
    min_longitude, max_longitude = -134, -117
    min_latitude, max_latitude = 32, 50
    key_words = {
        "standard_name": "sea_water_ph_reported_on_total_scale",
        "min_longitude": min_longitude,
        "max_longitude": max_longitude,
        "min_latitude": min_latitude,
        "max_latitude": max_latitude,
        "min_time": datetime.strftime(start_time, time_format),
        "max_time": datetime.strftime(end_time, time_format),
        "cdm_data_type": "TimeSeries"
    }
    erddap_builder = ERDDAP(
        server=server_id,
        protocol='tabledap'
    )
    search_url = erddap_builder.get_search_url(response="csv", **key_words)
    locations = pd.read_csv(search_url)
    locations.rename(
        columns = {
            "Dataset ID": "station_id",
            "Institution": "source",
            "Title": "name"
        },
        inplace = True
    )
    locations["provider"] = server_id
    locations = locations[["station_id", "name", "source", "provider"]]
    return locations


def get_data(
    server_id,
    start_date=None,
    end_date=None,
    dataset_id=None
):
    """ Retrieves data from input server and time range as DataFrame.
    
    Args:
        server_id (str): URL of ERDDAP server
        dataset_id (str): id of dataset hosted on input server_id. If
            None, will retrieve all relevant datasets on server.
        start_date (MM/DD/YYYY): Default None. If none supplied,
            starts with two years ago.
        end_date (MM/DD/YYYY): Default None. If none, uses current date.
    Returns:
        pd.DataFrame: Contains information on all platforms listed in the input csv.
    """
    erddap_time = "%m/%d/%Y"
    if start_date is None:
        start_date = (datetime.now() - timedelta(weeks=104))
    else:
        start_date = datetime.strptime(start_date, erddap_time)
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, erddap_time)
    if dataset_id is None:
        locations = get_location_data(server_id, start_date, end_date)
        dataset_ids = locations['station_id'].tolist()
    else:
        dataset_ids = [dataset_id]

    all_datasets = []
    for dataset_id in dataset_ids:
        erddap_builder = ERDDAP(
            server=server_id,
            protocol="tabledap",
        )

        erddap_builder.response = "csv"
        erddap_builder.dataset_id = dataset_id
        erddap_builder.constraints = {
            "time>=": "{}".format(start_date.strftime("%m/%d/%Y")),
            "time<=": "{}".format(end_date.strftime("%m/%d/%Y")),
        }
        dataset_df = erddap_builder.to_pandas()
        dataset_df['station_id'] = dataset_id
        all_datasets.append(dataset_df)
    server_df = pd.concat(all_datasets)
    return server_df




def format_df(df):
    df = df.set_index(['time (UTC)', 'latitude (degrees_north)', 'longitude (degrees_east)', 'z (m)', 'station_id'])
    df = df.drop(
        ['Unnamed: 0', 'Unnamed: 0.1', 'mass_concentration_of_oxygen_in_sea_water (mL.L-1)', 'mass_concentration_of_oxygen_in_sea_water (micromol.L-1)'],
        axis='columns',
        errors='ignore'
    )
    df.columns = df.columns.str.split(' ', 1).str[0]
    df.columns = df.columns.str.split('_qc_', 1, expand=True)
    df.rename(columns=COL_RENAMES, inplace=True, errors='ignore')
    df = pd.melt(df, ignore_index=False, var_name=['parameter', 'meta'])
    df = df.reset_index().rename(columns=COL_RENAMES, errors='ignore')
    df = df.drop_duplicates()
    df = df.pivot(
        index=['datetime', 'latitude', 'longitude', 'z', 'station_id', 'parameter'],
        columns=['meta'],
        values=['value']
    )
    df.columns = ["value", "qc_agg", "qc_tests"]
    df = df.dropna(subset=['value'])
    return df


if __name__ == "__main__":
    servers = ["https://erddap.dataexplorer.oceanobservatories.org/erddap/", "https://erddap.cencoos.org/erddap/"]
    df = get_data(server_id=servers[0], start_date="01/11/2022")
    format_df(df).to_csv("sample.csv")