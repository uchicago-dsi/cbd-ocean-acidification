from datetime import datetime, timedelta
from urllib.error import HTTPError
import pandas as pd
import numpy as np
import erddapy
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

class ERDDAP():

    time_format = "%m/%d/%Y"

    def __init__(self, server_id):
        self.server_id = server_id

    def get_location_data(
            self,
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
        erddap_builder = erddapy.ERDDAP(
            server=self.server_id,
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
        locations["provider"] = self.server_id
        locations = locations[["station_id", "name", "source", "provider"]]
        return locations

    def get_data(
        self,
        dataset_id,
        start_date,
        end_date        
    ):
        """ Retrieves data from input server and time range as DataFrame.
        
        Args:
            dataset_id (str): id of dataset hosted on input server_id.
            start_date (datetime): Earliest time to retrieve measurements from
            end_date (datetime): Latest time to retrieve measurements from
        Returns:
            pd.DataFrame: Contains information on all platforms listed in the input csv.
        """
        erddap_builder = erddapy.ERDDAP(
            server=self.server_id,
            protocol="tabledap",
        )

        erddap_builder.response = "csv"
        erddap_builder.dataset_id = dataset_id
        erddap_builder.constraints = {
            "time>=": "{}".format(start_date.strftime(self.time_format)),
            "time<=": "{}".format(end_date.strftime(self.time_format)),
        }
        dataset_df = erddap_builder.to_pandas()
        dataset_df['station_id'] = dataset_id
        long_df = self.format_df(dataset_df)
        return long_df

    def format_df(self, df):
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
