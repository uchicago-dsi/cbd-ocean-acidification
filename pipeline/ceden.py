# -*- coding: utf-8 -*-
from pipeline import utils
import pandas as pd
from datetime import datetime
import numpy as np
from pathlib import Path
from pytemp import pytemp  # for temperature unit conversion
import time

pd.options.mode.chained_assignment = None  # default='warn'

HERE = Path(__file__).resolve().parent
stations = HERE / "metadata" / "stations.csv"

# .xls does not allow more than 63356 rows
MAX_EXCEL_SIZE = 65535

location_columns = {
    "latitude": "ActualLatitude",
    "longitude": "ActualLongitude",
    "horizontal_datum": "Datum",
    "ceden_id": "StationCode",
    "horizontal_coordinate_collection": "CoordinateSource",
    "ceden_project_code": "ProjectCode",
    "source": "AgencyCode"
}

results_columns = {
    "instrument": "CollectionDeviceName",
    "station_id": "StationCode",
    "parameter": "AnalyteName",
    "value": "Result",
    "unit": "UnitName",
    "quality": "QACode",
    "depth": "CollectionDepth",
    "depth_unit": "UnitCollectionDepth",
    "method": "MethodName",
}

parameter_dict = {
    "salinity": "Salinity",
    "total_alkalinity": "Alkalinity as CaCO3",
    "water_temperature": "Temperature",
    "oxygen_concentration": "Oxygen, Dissolved",
    "oxygen_saturation": "Oxygen, Saturation",
    "co2": "Carbon dioxide, free",
    "water_pressure": "Pressure",
    "air_pressure": "Barometric Pressure",
    "air_temperature": "Temperature",  # looks like same as water
    "tco2": "Carbon dioxide, free",
    "pH": "pH",
}
class CEDEN():
    state = "California"
    instructions = """California Submission Instructions
    Before you run the pipeline, you should have:
     - Create an IR Portal account: https://public2.waterboards.ca.gov/IRPORTAL/Account/Register
     - Ensure all stations you wish to submit have the required information in `stations.csv` and `station_parameter_metadata.csv`
    After running the pipeline:
     - Results should be saved here: {}
     - Submit results to the IR Portal
    """

    def __init__(self):
        """ initialize with proper output directory """
        request_time = datetime.now().strftime("%Y-%m-%dT%H-%M")
        self.results_directory = HERE.parent / "output" / self.state / request_time
        self.results_directory.mkdir(exist_ok=True, parents=True)

    def format_data_for_agency(self, data: pd.DataFrame) -> Path:
        """ Outermost method for transforming data into agency ready format
        
        Args:
            data: data from collector subclass in standardized format 
        Returns:
            nothing. Creates directory with results.
        """
        split_n = data.shape[0] // MAX_EXCEL_SIZE + 1
        dfs = np.array_split(data, split_n)

        for batch_no, df in enumerate(dfs):
            stations_table = pd.read_csv(stations, index_col="station_id")
            stations_used = df["station_id"].unique()
            stations_subset = stations_table[stations_table.index.isin(stations_used)]
            locations = self.populate_locations(stations_subset)
            results = self.populate_field_results(df)
            location_file = self.results_directory / "cbd_locations_b{}.csv".format(batch_no)
            locations.to_csv(location_file)
            results_file = self.results_directory / "cbd_results_b{}.csv".format(batch_no)
            results.to_csv(results_file)

        # create instructions
        with open(self.results_directory / "README.txt", "w") as f:
            f.write(self.instructions.format(self.results_directory))

        return self.results_directory

    def populate_locations(self, df: pd.DataFrame):
        """ Processes California data to match CEDEN template restrictions.

        Args:
            df (DataFrame): Contains the merged columns of 'measurements' 
                and 'stations' tables for California stations. 
            
        Returns:
            locations_dataframe
        """
        df = df.reset_index()
        df["ceden_id"] = np.where(df["ceden_id"], df["ceden_id"], df["station_id"])
        # Preprocess the dataframe to match CEDEN format
        df = df[
            ["ceden_id", "latitude", "longitude", "source", "horizontal_datum", "ceden_project_code", "horizontal_coordinate_collection"]
        ]
        df.rename(columns=location_columns, inplace=True, errors="ignore")
        df["CoordinateNumber"] = 1
        df["LocationCode"] = "Not Recorded"
        df["EventCode"] = "WQ"
        df["ProtocolCode"] = "Not Recorded"
        df["GeometryShape"] = "Point"

        df = df.loc[:, df.columns.isin(
            [
                "StationCode",
                "SampleDate",
                "ProjectCode",
                "EventCode",
                "ProtocolCode",
                "AgencyCode",
                "SampleComments",
                "LocationCode",
                "GeometryShape",
                "CoordinateNumber",
                "ActualLatitude",
                "ActualLongitude",
                "Datum",
                "CoordinateSource",
                "Elevation",
                "UnitElevation",
                "StationDetailVerBy",
                "StationDetailVerDate",
                "StationDetailComments",
            ]
        )]

        return df


    def populate_field_results(self, df):
        """ Processes California data to match CEDEN template restrictions.

        Args:
            df (DataFrame): Contains the merged columns of 'measurements' 
                and 'stations' tables for California stations.             
        Returns:
            field_results dataframe
        """
        stations_table = pd.read_csv(stations)
        stations_table["ceden_id"] = np.where(
            stations_table["ceden_id"],
            stations_table["ceden_id"], 
            stations_table["station_id"]
        )
        df["station_id"] = df["station_id"].map(stations_table.set_index("station_id")["ceden_id"])
        df["CollectionTime"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%H:%M")
        df["SampleDate"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%d/%m/%Y")
        df["MatrixName"] = df["parameter"].map(utils.ceden_matrix_dict)
        df["Replicate"] = df.groupby(["station_id", "SampleDate"]).cumcount() + 1
        df["instrument"] = np.where(df["instrument"], df["instrument"], "Not Recorded")
        df["method"] = np.where(df["method"], df["method"], "FieldMeasure")

        molg = df.loc[df.unit == "µmol/kg", "value"] * 1000
        df.loc[df.unit == "µmol/kg", "value"] = molg

        deg_c = df.loc[df.unit == "F", "value"].apply(lambda x: pytemp(x, "f", "c"))
        df.loc[df.unit == "F", "value"] = deg_c

        mmhg = df.loc[df.unit == "inHg", "value"] / 0.0393701
        df.loc[df.unit == "inHg", "value"] = mmhg

        for k, v in utils.ceden_field_misc.items():
            df.loc[:, k] = v

        
        df["unit"] = df["unit"].map(utils.ceden_unit_dict)
        df["parameter"] = df["parameter"].map(parameter_dict)
        df.sort_values(["station_id", "parameter", "datetime"])
        df.rename(columns=results_columns, inplace=True, errors="ignore")
        df = df.loc[:, df.columns.isin(
            [
                "StationCode",
                "SampleDate",
                "ProjectCode",
                "EventCode",
                "ProtocolCode",
                "AgencyCode",
                "SampleComments",
                "LocationCode",
                "GeometryShape",
                "CollectionTime",
                "CollectionMethodCode",
                "Replicate",
                "CollectionDeviceName",
                "CollectionDepth",
                "UnitCollectionDepth",
                "PositionWaterColumn",
                "FieldCollectionComments",
                "MatrixName",
                "MethodName",
                "AnalyteName",
                "FractionName",
                "UnitName",
                "FieldReplicate",
                "Result",
                "ResQualCode",
                "QACode",
                "ComplianceCode",
                "BatchVerificationCode",
                "CalibrationDate",
                "FieldResultComments",
            ]
        )]
        return df
