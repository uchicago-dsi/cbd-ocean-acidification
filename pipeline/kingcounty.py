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
    "Qual_SeaFET_Internal_pH_raw",
    "SeaFET_Internal_pH_raw",
    "Qual_SeaFET_External_pH_recalc_w_salinity",
    "SeaFET_External_pH_recalc_w_salinity",
    "Qual_SeaFET_External_pH_final_recalc",
    "SEAFET_EXT_PH_V",
    "Qual_SeaFET_Internal_pH_recalculated",
    "SEAFET_INT_PH_V",
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
    "SeaFET_Internal_pH_raw": "Measure_SeaFET_Internal_pH_raw",
    "SeaFET_External_pH_recalc_w_salinity": "Measure_SeaFET_External_pH_recalc_w_salinity",
    "SEAFET_EXT_PH_V": "Measure_SeaFET_External_pH_final_recalc",
    "SEAFET_INT_PH_V": "Measure_SeaFET_Internal_pH_recalculated",
    "Salinity_PSU": "Measure_Salinity",
    "Depth_m": "depth",
}


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
    url = "https://green2.kingcounty.gov/marine-buoy/Data.aspx"
    param_path = os.path.abspath(
        os.path.join(
            PATH, "..", "..", "data", "king-county", "keys", "king-county-keys.json"
        )
    )

    if not end_date:
        current_time = datetime.now()
        end_date = current_time.strftime("%m/%d/%Y")
    if not start_date:
        start_date = "01/01/1900"

    # Setting up the parameters for POST request
    with open(param_path) as f:
        params = json.load(f)

    start_date_key = "ctl00$kcMasterPagePlaceHolder$startDate"
    end_date_key = "ctl00$kcMasterPagePlaceHolder$endDate"

    # Iterate over station parameters
    cols = set()
    dfs = []
    for buoy, data in tqdm(params.items()):
        data[start_date_key] = start_date
        data[end_date_key] = end_date
        response = requests.post(url, data=data)
        tsv = response.text.split("***END***")[1]
        df = pd.read_csv(StringIO(tsv), sep="\t", low_memory=False)
        df["station_id"] = buoy
        df.dropna(how="all", axis=1, inplace=True)

        # Seattle Aquarium gets two measurements at different depths for each
        # parameter, and these are shown on the same row with different column names.
        if buoy == "SEATTLE_AQUARIUM":
            pd.options.mode.chained_assignment = None
            sa_1 = df.filter(regex="1_|Date|station_id")
            sa_2 = df.filter(regex="2_|Date|station_id")
            sa_rename_1 = {i: i.replace("1_", "") for i in sa_1.columns}
            sa_rename_2 = {i: i.replace("2_", "") for i in sa_2.columns}
            sa_1.rename(columns=sa_rename_1, inplace=True)
            sa_2.rename(columns=sa_rename_2, inplace=True)
            df = pd.concat([sa_1, sa_2], ignore_index=True)

        dfs.append(df)
    all_measures = pd.concat(dfs)
    all_measures = all_measures.filter(items=COLS)
    all_measures["Qual_Dissolved_Oxygen_Sat"] = all_measures["Qual_DO"]
    all_measures["Qual_Dissolved_Oxygen"] = all_measures.pop("Qual_DO")
    all_measures.rename(columns=COL_RENAMES, inplace=True)
    all_measures = pd.wide_to_long(
        all_measures,
        stubnames=["Measure", "Qual"],
        i=["date_time", "station_id", "depth"],
        j="parameter",
        suffix=r"\w+",
        sep="_",
    ).reset_index()
    all_measures.dropna(subset=["Measure"], inplace=True)
    all_measures.rename(
        columns={"Qual": "quality_flag", "Measure": "value"}, inplace=True
    )
    all_measures["depth_unit"] = "m"
    all_measures["date_time"] = pd.to_datetime(all_measures.date_time)
    return all_measures


if __name__ == "__main__":
    df = get_data(start_date="03/23/2021", end_date="9/27/2021")
    data_path = os.path.abspath(
        os.path.join(
            PATH,
            "..",
            "..",
            "data",
            "king-county",
            "king_county_data_{}.csv".format(str(int(time.time()))),
        )
    )
    df.to_csv(data_path, index=False)
