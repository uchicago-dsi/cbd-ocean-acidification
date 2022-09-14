from datetime import datetime, timedelta
from urllib.error import HTTPError
import pandas as pd
import numpy as np
import erddapy
import requests
from pathlib import Path
from pipeline import utils


index_columns = ["datetime", "latitude", "longitude", "station_id", "depth"]

HERE = Path(__file__).resolve().parent
station_parameter_metadata = HERE / 'metadata' / 'station_parameter_metadata.csv'

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
        long_df = self.standardize_data(dataset_df)
        return long_df

    def filter_poor_data(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """Remove suspect / poor quality data"""
        dataset["suspect"] = (dataset["quality"] >= 3)
        return dataset[~dataset["suspect"]]

    def standardize_data(self, dataset: pd.DataFrame):
        """ Reformat data to match a single standard format """
        # use station_id column used to retrieve data
        dataset.drop(columns=["station"], inplace=True)
        dataset.rename(columns=utils.positional_column_mapping, inplace=True, errors='ignore')
        # measurements updated with qc tests, keep most up to date
        dataset.drop_duplicates(subset=index_columns, keep="last", inplace=True)
        # rearrange stubs to prefix parameter names to fit wide_to_long
        # erddap cols are var_name_qc_agg, var_name_qc_tests, var_name (unit)
        dataset.columns = dataset.columns.str.replace("(.*) \(.*\)", "value_\\1", regex=True)
        dataset.columns = dataset.columns.str.replace("(.*)_qc(.*)", "qc\\2_\\1", regex=True)
        long_df = pd.wide_to_long(
            dataset,
            stubnames=["value", "qc_agg", "qc_tests"],
            i=index_columns, 
            j="parameter",
            sep="_",
            suffix=r"\w+"
        )
        long_df.drop(columns="qc_tests", inplace=True)
        long_df.dropna(subset=['value'], inplace=True)
        long_df.rename(columns={"qc_agg": "quality"}, inplace=True)
        long_df.reset_index(inplace=True)
        parameter_metadata = pd.read_csv(station_parameter_metadata, index_col=["station_id", "parameter"])
        long_df = long_df.join(parameter_metadata, on=["station_id", "parameter"], how='left')
        long_df['parameter'] = long_df["parameter"].map(utils.parameter_dict)
        long_df["depth_unit"] = "m"
        long_df = self.filter_poor_data(long_df)
        return long_df
