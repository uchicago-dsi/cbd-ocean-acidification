

from pytest import param
from suds.client import Client
from datetime import datetime, timedelta
from urllib.error import HTTPError
import pandas as pd
import numpy as np
import erddapy
import requests
from pathlib import Path
from pipeline import utils
from bs4 import BeautifulSoup


index_columns = ["datetime", "station_id", "depth"]

HERE = Path(__file__).resolve().parent
station_parameter_metadata = HERE / 'metadata' / 'station_parameter_metadata.csv'
stations = HERE / "metadata" / "stations.csv"

class NERRS():

    api_endpoint = "http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl"
    time_format = "%Y-%m-%d"

    def get_data(
        self,
        dataset_id,
        start_date,
        end_date
    ):
        """ Retrieves data from input server and time range as dataframe """
        start_date = start_date.strftime(self.time_format)
        end_date = end_date.strftime(self.time_format)
        soapClient = Client(self.api_endpoint, timeout=90, retxml=True)

        raw_data = soapClient.service.exportAllParamsDateRangeXMLNew(dataset_id, start_date, end_date, '*')
        xml_data = BeautifulSoup(raw_data, "lxml")
        records = []
        for data_tag in xml_data.find_all("data"):
            record = {}
            for param_tag in data_tag.children:
                if param_tag.text == "\n" or param_tag.contents == []:
                    continue
                record[param_tag.name] = param_tag.text
            records.append(record)
        dataset_df = pd.DataFrame(records)
        dataset_df["station_id"] = dataset_id
        long_df = self.standardize_data(dataset_df)
        return long_df


    def standardize_data(self, dataset: pd.DataFrame):
        """ Reformat data to match single standard format """
        desired_columns = [
            "temp", "f_temp", "ec_temp",
            "ph", "f_ph", "ec_ph",
            "turb", "f_turb", "ec_turb",
            "do_mgl", "f_do_mgl", "ec_do_mgl",
            "do_pct", "f_do_pct", "ec_do_pct",
            "sal", "f_sal", "ec_sal",
            "spcond", "f_spcond", "ec_spcond",
            "utcstamp", "level", "station_id"
        ]
        dataset = dataset.loc[:, dataset.columns.isin(desired_columns)]
        dataset.rename(columns=utils.positional_column_mapping, inplace=True, errors='ignore')
        dataset.drop_duplicates(subset=index_columns, keep="last", inplace=True)
        # rearrange stubs to prefix parameter names to fit wide_to_long
        # nerrs cols are var_name, f_var_name, ec_var_name
        dataset.columns = dataset.columns.str.replace("(^(?!ec_|f_|station|datetime|depth)(.*))", "value_\\1")       
        long_df = pd.wide_to_long(
            dataset,
            stubnames=["value", "ec", "f"],
            i=index_columns, 
            j="parameter",
            sep="_",
            suffix=r"\w+"
        )
        long_df.drop(columns="ec", inplace=True)
        long_df.dropna(subset=['value'], inplace=True)
        long_df.rename(columns={"f": "quality"}, inplace=True)
        long_df.reset_index(inplace=True)
        parameter_metadata = pd.read_csv(station_parameter_metadata, index_col=["station_id", "parameter"])
        long_df = long_df.join(parameter_metadata, on=["station_id", "parameter"], how='left')
        stations_metadata = pd.read_csv(stations, index_col="station_id")
        stations_metadata = stations_metadata[["latitude", "longitude"]]
        long_df = long_df.join(stations_metadata, on="station_id", how="left")
        long_df['parameter'] = long_df["parameter"].map(utils.parameter_dict)
        long_df["depth_unit"] = "m"
        return long_df