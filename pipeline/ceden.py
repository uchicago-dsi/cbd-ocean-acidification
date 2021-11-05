import utils
import pandas as pd
from xlrd import open_workbook
from xlutils.copy import copy
import os


def populate_locations(stations, measurements, locations):

    # Preprocess the dataframe to match CEDEN format
    cali_stations = stations.query('state == "California"')
    cali_stations = merge(measurements, on="station_id", how="inner")
    cali_stations["date"] = pd.to_datetime(
        cali_stations.date_time, utc=True
    ).dt.strftime("%d/%b/%Y")
    cali_stations = cali_stations[
        ["station_id", "latitude", "longitude", "date"]
    ].drop_duplicates()
    cali_stations["StationCode"] = cali_stations.pop("station_id").map(
        utils.ceden_stations
    )
    cali_stations = cali_stations.query("StationCode != ''")

    for k, v in utils.ceden_station_misc.items():
        cali_stations[k] = v

    cali_stations = cali_stations[
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
    iter_stations = cali_stations.reset_index(drop=True).iterrows()
    for i, cols in iter_rows:
        for j, value in enumerate(cols):
            locations.write(i + 1, j, value)


def populate_field_results(stations, measurements, field_results):
    pass


def populate_template(measurements_path, stations_path, template_path):
    measurements = pd.read_csv(measurements_path, parse_dates=["date_time"])
    stations = pd.read_csv(stations_path)
    rb = open_workbook(template_path, formatting_info=True)
    wb = copy(rb)
    locations = wb.get_sheet(1)
    field_results = wb.get_sheet(2)

    populate_locations(stations, measurements, locations)
    populate_field_results(stations, measurements, field_results)

    wb.save("template_stations.xls")


if __name__ == "__main__":
    PATH = os.path.abspath(__file__)
    measurements_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "ipacoa", "ipacoa_sample.csv")
    )
    stations_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "stations.csv")
    )
    template_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "templates", "ceden_field_template.xls")
    )

    populate_template(measurements_path, stations_path, template_path)

