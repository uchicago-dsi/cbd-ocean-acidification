import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import time
import os
import utils

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
    url = "http://www.ipacoa.org/ssa/get_platform_data.php"
    measurements_path = os.path.abspath(
        os.path.join(
            PATH, "..", "..", "data", "ipacoa", "lookups", "platform_measurements.csv"
        )
    )

    # Setting up parameters for GET request
    platform_measurement = pd.read_csv(measurements_path)

    # Filtering for measurements of interest
    platform_measurement = platform_measurement[platform_measurement["process"]]
    if station_id:
        station_mask = platform_measurement["platform_label"] == station_id
        platform_measurement = platform_measurement[station_mask]
    # Iterate over platform * measurement combinations
    dfs = []
    for i, (platform, measurement, process) in tqdm(
        platform_measurement.iterrows(), total=platform_measurement.shape[0]
    ):
        params = (
            ("platform_id", platform),
            ("var_id", measurement),
            ("data_type", "csv"),
        )
        response = requests.get(url, params=params)

        # Raise error if request is not successful
        response.raise_for_status()

        if response.text == "":
            continue
        df = pd.read_csv(StringIO(response.text))
        df["station_id"] = platform
        df["value"] = df.pop(df.columns[2])
        df["parameter"] = measurement
        df["depth_unit"] = "ft"
        df.rename(
            columns={" Depth (Ft)": "depth", "Date and Time": "date_time"},
            inplace=True,
        )
        df["depth"] = df["depth"].str.strip(" ft").astype(int)
        dfs.append(df)

    all_measures = pd.concat(dfs, ignore_index=True)
    all_measures["date_time"] = pd.to_datetime(
        all_measures["date_time"], errors="coerce"
    )
    if start_date:
        start_date = pd.to_datetime(start_date, utc=True)
        all_measures = all_measures[all_measures["date_time"] >= start_date]
    if end_date:
        end_date = pd.to_datetime(end_date, utc=True)
        all_measures = all_measures[all_measures["date_time"] <= end_date]

    # Add measurement units
    unit_path = os.path.abspath(
        os.path.join(
            PATH, "..", "..", "data", "ipacoa", "lookups", "measurement_lookup.csv"
        )
    )
    units = pd.read_csv(unit_path)
    all_measures = all_measures.merge(
        units[["parameter", "unit"]], on="parameter", how="left"
    )
    all_measures = all_measures[
        ["station_id", "date_time", "parameter", "value", "unit", "depth", "depth_unit"]
    ]

    # map parameter names to normalized names
    all_measures["parameter"] = all_measures["parameter"].map(utils.parameter_dict)

    return all_measures


if __name__ == "__main__":
    df_all = get_data()
    data_path = os.path.abspath(
        os.path.join(
            PATH,
            "..",
            "..",
            "data",
            "ipacoa",
            "ipacoa_data_{}.csv".format(str(int(time.time()))),
        )
    )
    df_all.to_csv(data_path, index=False)
