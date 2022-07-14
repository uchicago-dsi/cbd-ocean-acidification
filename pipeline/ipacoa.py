from readline import parse_and_bind
import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import time
from datetime import date
from pathlib import Path
from pipeline import utils

HERE = Path(__file__).resolve().parent
measurements_path = HERE / 'metadata' / 'ipacoa_platform_measurements.csv'
stations = HERE / "metadata" / "stations.csv"
station_parameter_metadata = HERE / 'metadata' / 'station_parameter_metadata.csv'

class IPACOA():

    def get_data(self, station_id, start_date, end_date):
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
            # change temps to celcius (ipacoa default is F)
            if "Temp" in measurement:
                df["value"] = (df["value"] - 32) * 5 / 9
            df.rename(
                columns={" Depth (Ft)": "depth", "Date and Time": "datetime"},
                inplace=True,
            )
            df["depth"] = df["depth"].str.strip(" ft").astype(int)
            dfs.append(df)

        all_measures = pd.concat(dfs, ignore_index=True)
        all_measures["datetime"] = pd.to_datetime(
            all_measures["datetime"], errors="coerce", utc=True
        )
        if start_date:
            start_date = pd.to_datetime(start_date, utc=True)
            all_measures = all_measures[all_measures["datetime"] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date, utc=True)
            all_measures = all_measures[all_measures["datetime"] <= end_date]

        all_measures = all_measures[
            ["station_id", "datetime", "parameter", "value", "depth", "depth_unit"]
        ]

        # add station metadata (location)        
        stations_df = pd.read_csv(stations, index_col="station_id")
        stations_df = stations_df[["latitude", "longitude"]]
        long_df = all_measures.join(stations_df, on="station_id", how="left")

        # map parameter names to device names, normalized names, and units
        parameter_metadata = pd.read_csv(station_parameter_metadata, index_col=["station_id", "parameter"])
        # if pd.merge(left=long_df, right=parameter_metadata, on=["station_id", "parameter"], indicator=True)
        
        long_df = long_df.join(parameter_metadata, on=["station_id", "parameter"], how='left')
        long_df["parameter"] = long_df["parameter"].map(utils.parameter_dict)

        # ipacoa has no quality flags
        long_df["quality"] = None

        return long_df
