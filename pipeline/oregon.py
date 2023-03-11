from .formatter import Formatter
from pathlib import Path
import pandas as pd
import numpy as np
import pytemp

HERE = Path(__file__).resolve().parent
stations = HERE / "metadata" / "stations.csv"

location_columns = {
    "station_id": "Monitoring Location ID",
    "name": "Monitoring Location Name",
    "setting" : "Monitoring Location Type",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "horizontal_datum" : "Horizontal Datum",
    "horizontal_coordinate_collection" : "Coordinate Collection Method",
    "tribal_land" : "Tribal Land Indicator",
}

results_columns = {
   "station_id": "Monitoring Location ID",
   # deal with activity start date and time in func
   # ?? : "Equipment ID",
   "parameter": "Characteristic Name",
   "value": "Result Value",
   "unit": "Result Unit",
   "quality": "Result Status ID",
}

parameter_dict = {
    "air_temperature": "Temperature, air",
    "water_temperature": "Temperature, water",
    "oxygen_concentration": "Dissolved oxygen (DO)",
    "oxygen_saturation": "Dissolved oxygen saturation",
    "salinity": "Salinity",
    "pH": "pH",
}

unit_dict = {
    "°F": "deg C",  # convert to celsius
    "mg/L": "mg/l",
    "%": "%",
    "µmol/kg": "umol/kg",
    "inHg": "mmHg", # convert to mm
    "PSU": "PSU",
}


qa_dict = {
    ## ?? : "Accepted" # reported result has been accepted
    ## ?? : "Validated" # reported result has been verified and reviewed
}

class Oregon(Formatter):
    state = "Oregon"
    instructions = """Oregon Submission Guidelines
    Before you run the pipeline, you should have:
      - Created a project plan, described [here](https://www.oregon.gov/deq/wq/Documents/irDataSubGuide.pdf) containing:
        - purpose statement
        - number of samples collected
        - qa/qc protocols
      - Fill out all relevant information on stations you are submitting
      - Set "Approved" to TRUE in stations.csv for stations you wish to submit and have recieved relevant approvals for.
    """


    def format_data_for_agency(self, data: pd.DataFrame) -> Path:
        stations_table = pd.read_csv(stations, index_col="station_id")
        stations_used = data["station_id"].unique()
        stations_subset = stations_table[stations_table.index.isin(stations_used)]
        locations = self.populate_locations(stations_subset)
        results = self.populate_field_results(data)
        location_file = self.results_directory / "cbd_locations.csv"
        locations.to_csv(location_file)
        results_file = self.results_directory / "cbd_results.csv"
        results.to_csv(results_file)

        # create instructions
        with open(self.results_directory / "README.txt", "w") as f:
            f.write(self.instructions.format(self.relative_path))

        return self.results_directory


    def populate_locations(self, df: pd.DataFrame):
        """ Processes Oregon data to match DEQ template restrictions.

        Args:
            df (DataFrame): Contains the merged columns of 'measurements' 
                and 'stations' tables for Oregon stations. 
            
        Returns:
            locations_dataframe
        """
        df = df.reset_index()
        df.rename(columns=location_columns, inplace=True, errors="ignore")
        df["Coordinate Collection Method"] = np.where(df["Coordinate Collection Method"], df["Coordinate Collection Method"], "Unknown")
        df = df.loc[:, df.columns.isin(
            [
                "Monitoring Location ID",
                "Monitoring Location Name",
                "Monitoring Location Type",
                "Monitoring Location Latitude",
                "Monitoring Location Longitude",
                "Horizontal Datum",
                "Coordinate Collection Method",
                "Tribal Land Indicator",
            ]
        )]

        return df

    def populate_field_results(self, df):
        """ Processes Oregon data to match DEQ template restrictions.

        Args:
            df (DataFrame): Contains the merged columns of 'measurements' 
                and 'stations' tables for Oregon stations.             
        Returns:
            field_results dataframe
        """
        stations_table = pd.read_csv(stations)
        df["Activity Start Date"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%Y/%m/%d") 
        df["Activity Start Time"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%H:%M") 
        # TODO: lookup equipment ids from saved table

        molg = df.loc[df.unit == "µmol/kg", "value"] * 1000
        df.loc[df.unit == "µmol/kg", "value"] = molg

        deg_c = df.loc[df.unit == "F", "value"].apply(lambda x: pytemp(x, "f", "c"))
        df.loc[df.unit == "F", "value"] = deg_c

        mmhg = df.loc[df.unit == "inHg", "value"] / 0.0393701
        df.loc[df.unit == "inHg", "value"] = mmhg

        df["unit"] = df["unit"].map(unit_dict)
        df["parameter"] = df["parameter"].map(parameter_dict)
        # TODO: ignore errors in map. If not by default, do map on filtered df with unit strat above
        df["quality"] = df["quality"].map(qa_dict)
        df.sort_values(["station_id", "parameter", "datetime"])
        df.rename(columns=results_columns, inplace=True, errors="ignore")
        df = df.loc[:, df.columns.isin(
            [
                "Monitoring Location ID",
                "Activity Start Date",
                "Activity Start Time",
                "Activity Time Zone",
                "Equipment ID",
                "Characteristic Name",
                "Result Value",
                "Result Unit",
                "Result Status ID",
            ]
        )]
        return df
