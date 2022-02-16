import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
from pathlib import Path
import json
from datetime import datetime, date, timedelta
import time
import re
from . import utils
HERE = Path(__file__).resolve().parent
KEYS = HERE / "metadata" / 'king-county-keys.json'

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

COL_RENAMES = {
    "Date": "date_time",
    "Air_Pressure_inHg": "Measure_Air_Pressure",
    "Air_Temperature_F": "Measure_Air_Temperature",
    "Dissolved_Oxygen_%Sat": "Measure_Dissolved_Oxygen_Sat",
    "Dissolved_Oxygen_mg/L": "Measure_Dissolved_Oxygen",
    "Water_Temperature_degC": "Measure_Water_Temperature",
    "SeaFET_Temperature_degC": "Measure_SeaFET_Temperature",
    "Sonde_pH": "Measure_Sonde_pH",
    "SeaFET_External_pH_recalc_w_salinity": "Measure_SeaFET_External_pH_recalc_w_salinity",
    "Salinity_PSU": "Measure_Salinity",
    "Depth_m": "depth",
}

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

        station_data = station_data.filter(items=COLS)
        station_data["Qual_Dissolved_Oxygen_Sat"] = station_data["Qual_DO"]
        station_data["Qual_Dissolved_Oxygen"] = station_data.pop("Qual_DO")
        station_data.rename(columns=COL_RENAMES, inplace=True)
        station_data.reset_index(inplace=True)
        station_data["id"] = station_data.index
        station_data = pd.wide_to_long(
            station_data,
            stubnames=["Measure", "Qual"],
            i=["id", "date_time", "station_id", "depth"],
            j="parameter",
            suffix=r"\w+",
            sep="_",
        ).reset_index()
        station_data.drop(["id", "index"], axis=1, inplace=True)
        station_data.dropna(subset=["Measure"], inplace=True)
        station_data.rename(
            columns={"Qual": "quality_flag", "Measure": "value"}, inplace=True
        )
        station_data["depth_unit"] = "m"
        station_data["date_time"] = pd.to_datetime(station_data.date_time)

        # map parameter names to device names, normalized names, and units
        station_data["device_name"] = station_data["parameter"].map(utils.kc_devices)
        station_data["parameter"] = station_data["parameter"].map(utils.parameter_dict)
        station_data["unit"] = station_data["parameter"].map(utils.kc_units)

        return station_data
