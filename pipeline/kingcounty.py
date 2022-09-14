import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
from pathlib import Path
import json
from datetime import datetime, date, timedelta
import time
import re
from pipeline import utils


HERE = Path(__file__).resolve().parent
KEYS = HERE / "metadata" / 'king-county-keys.json'
station_parameter_metadata = HERE / 'metadata' / 'station_parameter_metadata.csv'
stations = HERE / "metadata" / "stations.csv"

COLS = [
    "station_id",
    "Date",
    "Qual_Air_Pressure",
    "Air_Pressure_inHg",
    "Qual_Air_Temperature",
    "Air_Temperature_F",
    "Qual_DO",
    "Dissolved_Oxygen_%Sat",
    "Dissolved_Oxygen_mg/L",
    "Qual_Water_Temperature",
    "Water_Temperature_degC",
    "Qual_SeaFET_Temperature",
    "SeaFET_Temperature_degC",
    "Qual_Sonde_pH",
    "Sonde_pH",
    "Qual_SeaFET_External_pH_recalc_w_salinity",
    "SeaFET_External_pH_recalc_w_salinity",
    "Qual_Salinity",
    "Salinity_PSU",
    "Depth_m",
]

class KingCounty():
    time_format = "%m/%d/%Y"

    def get_data(self, station_id, start_date, end_date):
        """ Retrieves data for input station(s) and time range as DataFrame.

        Args:
            station_id (str): id for station of interest
            start_date (datetime): earliest time from which to collect data
            end_date(datetime): latest time from which to collect data
        Returns:
            pd.DataFrame: Contains information on all platforms listed in the input json.
        """
        url = "https://green2.kingcounty.gov/marine-buoy/Data.aspx"

        # Setting up the parameters for POST request
        with open(KEYS) as f:
            params = json.load(f)

        start_date_key = "ctl00$kcMasterPagePlaceHolder$startDate"
        end_date_key = "ctl00$kcMasterPagePlaceHolder$endDate"

        data = params[station_id]
        data[start_date_key] = start_date.strftime(self.time_format)
        data[end_date_key] = end_date.strftime(self.time_format)
        response = requests.post(url, data=data)
        tsv = response.text.split("***END***")[1]
        station_data = pd.read_csv(StringIO(tsv), sep="\t", low_memory=False)
        station_data["station_id"] = station_id
        station_data.dropna(how="all", axis=1, inplace=True)

        # Seattle Aquarium gets two measurements at different depths for each
        # parameter, and these are shown on the same row with different column names.
        if station_id == "SEATTLE_AQUARIUM":
            pd.options.mode.chained_assignment = None
            sa_1 = station_data.filter(regex="1_|Date|station_id")
            sa_2 = station_data.filter(regex="2_|Date|station_id")
            sa_rename_1 = {i: i.replace("1_", "") for i in sa_1.columns}
            sa_rename_2 = {i: i.replace("2_", "") for i in sa_2.columns}
            sa_1.rename(columns=sa_rename_1, inplace=True)
            sa_2.rename(columns=sa_rename_2, inplace=True)
            station_data = pd.concat([sa_1, sa_2], ignore_index=True)
        long_df = self.standardize_data(station_data)
        return long_df

    def filter_poor_data(self, dataset: pd.DataFrame):
        """Remove data with low or suspect quality"""
        dataset["suspect"] = (dataset["quality"] // 100 >= 3)
        return dataset[~dataset["suspect"]]

    def standardize_data(self, dataset: pd.DataFrame):
        """ Reformat data to match a single standard format """
        dataset = dataset.filter(items=COLS)
        # Dissolved Oxygen measures share on qc column 'DO'
        dataset["Qual_Dissolved_Oxygen_Sat"] = dataset["Qual_DO"]
        dataset["Qual_Dissolved_Oxygen"] = dataset.pop("Qual_DO")
        # restructure columns for wide_to_long
        dataset.rename(columns=utils.positional_column_mapping, inplace=True)
        # kingcounty cols are Var_Name_Unit, Qual_Var_Name
        dataset.rename(columns={'Dissolved_Oxygen_%Sat': 'Dissolved_Oxygen_Sat_%'}, inplace=True)
        dataset.columns = dataset.columns.str.replace("(^(?!Qual).*)_pH", "\\1_pH_1", regex=True)
        dataset.columns = dataset.columns.str.replace("(^(?!Qual|[a-z]).*)_(.*)", "value_\\1", regex=True)
        dataset.columns = dataset.columns.str.replace("Qual_(.*)", "quality_\\1", regex=True)
        dataset.reset_index(inplace=True)
        long_df = pd.wide_to_long(
            dataset,
            stubnames=["value", "quality"],
            i=["datetime", "station_id", "depth"],
            j="parameter",
            suffix=r"\w+",
            sep="_",
        )
        long_df = long_df.reset_index()
        long_df.drop(columns="index", inplace=True)
        long_df.dropna(subset=["value"], inplace=True)
        # add final metadata
        long_df["depth_unit"] = "m"
        stations_df = pd.read_csv(stations, index_col="station_id")
        stations_df = stations_df[["latitude", "longitude"]]
        long_df = long_df.join(stations_df, on="station_id", how="left")

        # map parameter names to device names, normalized names, and units
        parameter_metadata = pd.read_csv(station_parameter_metadata, index_col=["station_id", "parameter"])
        long_df = long_df.join(parameter_metadata, on=["station_id", "parameter"], how='left')
        long_df["parameter"] = long_df["parameter"].map(utils.parameter_dict)
        long_df = self.filter_poor_data(long_df)

        return long_df
