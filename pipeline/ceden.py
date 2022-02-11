# -*- coding: utf-8 -*-

import utils
import pandas as pd
from xlrd import open_workbook
from xlutils.copy import copy
import os
import numpy as np
from pytemp import pytemp  # for temperature unit conversion
import time

pd.options.mode.chained_assignment = None  # default='warn'


def populate_locations(df, locations):
    """ Processes California data to match CEDEN template restrictions.
        Writes data to the template's 'Locations' sheet. Changes the existing
        sheet and does not return anything. 

    Args:
        df (DataFrame): Contains the merged columns of 'measurements' 
            and 'stations' tables for California stations. 
        locations (xlwt.Worksheet): Excel Worksheet object for the 'Locations' 
            sheet of the template. 
        
    Returns:
        None
    """

    # Preprocess the dataframe to match CEDEN format
    df = df[
        ["station_id", "latitude", "longitude", "date", "provider"]
    ].drop_duplicates()
    df["StationCode"] = df.pop("station_id").map(utils.ceden_stations)
    df["Datum"] = df["provider"].map(utils.ceden_datum_dict)

    for k, v in utils.ceden_station_misc.items():
        df.loc[:, k] = v

    df = df[
        [
            "StationCode",
            "date",
            "ProjectCode",
            "EventCode",
            "ProtocolCode",
            "AgencyCode",
            "SampleComments",
            "LocationCode",
            "GeometryShape",
            "CoordinateNumber",
            "latitude",
            "longitude",
            "Datum",
            "CoordinateSource",
            "Elevation",
            "UnitElevation",
            "StationDetailVerBy",
            "StationDetailVerDate",
            "StationDetailComments",
        ]
    ]

    # Write dataframe content to the 'Locations' sheet of CEDEN template
    iter_stations = df.reset_index(drop=True).iterrows()
    for i, cols in iter_stations:
        for j, value in enumerate(cols):
            locations.write(i + 1, j, value)


def populate_field_results(df, field_results):
    """ Processes California data to match CEDEN template restrictions.
        Writes data to the template's 'Field Results' sheet. Changes the existing
        sheet and does not return anything. 

    Args:
        df (DataFrame): Contains the merged columns of 'measurements' 
            and 'stations' tables for California stations. 
        field_results (xlwt.Worksheet): Excel Worksheet object for the 'Field results' 
            sheet of the template. 
        
    Returns:
        None
    """

    df["time"] = pd.to_datetime(df.date_time, utc=True).dt.strftime("%H:%M")
    df["Replicate"] = df.groupby(["station_id", "date"]).cumcount() + 1

    df["station_id"] = df["station_id"].map(utils.ceden_stations)

    molg = df.loc[df.unit == "µmol/kg", "value"] * 1000
    df.loc[df.unit == "µmol/kg", "value"] = molg

    deg_c = df.loc[df.unit == "°F", "value"].apply(lambda x: pytemp(x, "f", "c"))
    df.loc[df.unit == "°F", "value"] = deg_c

    mmhg = df.loc[df.unit == "inHg", "value"] / 0.0393701
    df.loc[df.unit == "inHg", "value"] = mmhg

    for k, v in utils.ceden_field_misc.items():
        df.loc[:, k] = v

    df["MatrixName"] = df["parameter"].map(utils.ceden_matrix_dict)
    df["unit"] = df["unit"].map(utils.ceden_unit_dict)
    df["parameter"] = df["parameter"].map(utils.ceden_param_dict)
    df.sort_values(["station_id", "parameter", "date_time"])
    df = df[
        [
            "station_id",
            "date",
            "ProjectCode",
            "EventCode",
            "ProtocolCode",
            "AgencyCode",
            "SampleComments",
            "LocationCode",
            "GeometryShape",
            "time",
            "CollectionMethodCode",
            "Replicate",
            "CollectionDeviceName",
            "depth",
            "depth_unit",
            "PositionWaterColumn",
            "FieldCollectionComments",
            "MatrixName",
            "MethodName",
            "parameter",
            "FractionName",
            "unit",
            "FieldReplicate",
            "value",
            "ResQualCode",
            "QACode",
            "ComplianceCode",
            "BatchVerificationCode",
            "CalibrationDate",
            "FieldResultComments",
        ]
    ]
    iter_measurements = df.reset_index(drop=True).iterrows()
    for i, cols in iter_measurements:
        for j, value in enumerate(cols):
            field_results.write(i + 1, j, value)


def populate_template(measurements_path, stations_path, template_path, submittal_path):
    """ Wrapper function to populate CEDEN template. Reads 'measurements' and 'stations' 
        tables as well as the empty CEDEN template and passes them as parameters to the
        populate_locations() and populate_field_results() functions.

    Args:
        measurements_path (str): Path to the measurements .csv file. 
        stations_path (str): Path to the stations .csv file. 
        template_path (str): Path to the empty CEDEN template (.xls).
        submittal_path (str): Path to the folder where the populated template is going to
            be saved.  
        
    Returns:
        None. Saves the populated template to the provided template_path.
    """
    measurements = pd.read_csv(measurements_path, parse_dates=["date_time"])
    stations = pd.read_csv(stations_path)

    cali_stations = stations.query('state == "California"')
    cali_stations = cali_stations.merge(measurements, on="station_id", how="inner")
    cali_stations.sort_values(["station_id", "parameter", "date_time"], inplace=True)
    cali_stations["date"] = pd.to_datetime(
        cali_stations.date_time, utc=True
    ).dt.strftime("%d/%b/%Y")

    # .xls does not allow more than 63356 rows
    max_rows = 65535
    split_n = cali_stations.shape[0] // max_rows + 1
    dfs = np.array_split(cali_stations, split_n)

    for df in dfs:
        rb = open_workbook(template_path, formatting_info=True)
        wb = copy(rb)
        locations = wb.get_sheet(1)
        field_results = wb.get_sheet(2)

        populate_locations(df, locations)
        populate_field_results(df, field_results)

        file_name = "ceden_{}.xls".format(str(int(time.time())))
        file_path = os.path.join(submittal_path, file_name)

        wb.save(file_path)


if __name__ == "__main__":
    PATH = os.path.abspath(__file__)

    measurements_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "measurements.csv")
    )
    stations_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "stations.csv")
    )
    template_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "templates", "ceden_field_template.xls")
    )
    submittal_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "submittal")
    )

    populate_template(measurements_path, stations_path, template_path, submittal_path)
