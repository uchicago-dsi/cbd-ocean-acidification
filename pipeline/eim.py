import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

HERE = Path(__file__).resolve().parent
stations = HERE / "metadata" / "stations.csv"

MAX_EIM_ROWS = 150000

location_columns = {
    "station_id": "Location ID",
    "name": "Location Name",
    "setting": "Location Setting",
    "description": "Location Description",
    "latitude": "Latitude Degrees",
    "longitude": "Longitude Degrees",
    "horizontal_datum": "Horizontal Datum",
    "horizontal_coordinate_accuracy": "Horizontal Coordinate Accuracy",
    "horizontal_coordinate_collection": "Horizontal Coordinate Collection Method"
}

results_columns = {
    "instrument": "Instrument ID",
    "station_id": "Location ID",
    "parameter": "Result Parameter Name",
    "value": "Result Value",
    "unit": "Result Unit",
    "quality": "Result Data Qualifier",
    "depth": "Field Collection Depth",
    "depth_unit": "Field Collection Depth Units",
    "method": "Result Method"
}

parameter_names = {
    "pH_salinity": "pH",
    "pH_internal": "pH",
    "pH_external": "pH",
    "water_temperature": "Temperature, water",
    "salinity": "Salinity",
    "water_pressure" : "Water pressure",
    "oxygen_saturation": "Dissolved Oxygen Percent Saturation",
    "oxygen_concentration": "Dissolved Oxygen",
    "conductivity": "Conductivity",
    "total_dissolved_solids": "Total Dissolved Solids",
    "turbidity": "Turbidity",
    "total_alkalinity": "Alkalinity, Total as CaCO3"
}

units = {
    "microg/L": "ug/L",
    "C": "deg C",
    "ntu": "NTU",
    "decibars": "dbars",
    "micromol/L": "umol/L",
    "inHg": "in/Hg"
}

class EIM():
    state = "Washington"

    instructions = """Washington Submission Steps
    Before you ran the pipeline, you should have:
     - Follow the instructins here (https://apps.ecology.wa.gov/eim/help/HelpDocuments/OpenDocument/14) 
       through creating the relevant studies
     - Update stations.csv to add the eim_study_id to the relevant stations
     - Ensure all stations you wish to submit have the required information 
       in stations.csv and station_parameter_metadata.csv
     - IMPORTANT: this will not work if the desired stations have not had
       their 'approved' value in stations.csv set to TRUE and an eim_study_id
       and eim_location_study added.
    After running the pipeline:
     - Results should be saved here: {}
     - Follow the instructions here (https://fortress.wa.gov/ecy/eimhelp/HelpDocuments/OpenDocument/13) to submit the generated data files in this directory. Note that each study will have its own subdirectory. 
    """


    def __init__(self):
        """ initialize with proper output directory """
        request_time = datetime.now().strftime("%Y-%m-%dT%H-%M")
        self.relative_path = Path("output") / self.state / request_time
        self.results_directory = HERE.parent / self.relative_path
        self.results_directory.mkdir(exist_ok=True, parents=True)

    def format_data_for_agency(self, data: pd.DataFrame) -> Path:
        """ Outermost method for transforming data into agency ready format
        
        Args:
            data: data from collector subclass in standardized format 
        Returns:
            path to directory with results.
        """
        stations_table = pd.read_csv(stations, index_col="station_id")
        stations_used = data["station_id"].unique()
        stations_subset = stations_table[stations_table.index.isin(stations_used)]
        stations_subset.reset_index(inplace=True) 
        if np.isnan(stations_subset["eim_study_id"].unique()):
            raise ValueError("No returned stations have an 'eim_study_id' in stations.csv")
        for study_id in stations_subset["eim_study_id"].unique():
            stations_used_by_study = stations_subset[stations_subset["eim_study_id"] == study_id]["station_id"].unique()
            self.save_results_for_study(data[data["station_id"].isin(stations_used_by_study)], study_id)
        
        # create instructions
        with open(self.results_directory / "README.txt", "w") as f:
            f.write(self.instructions.format(self.relative_path))

        return self.results_directory
        

    def save_results_for_study(self, data: pd.DataFrame, study_id: str):
        """ Saves results for a single EIM study"""
        # 150,000 records per batch. 1 study + location per batch
        study_result_directory = self.results_directory / str(study_id)
        study_result_directory.mkdir(exist_ok=True)
        stations_table = pd.read_csv(stations, index_col="station_id")
        stations_used = data["station_id"].unique()
        stations_subset = stations_table[stations_table.index.isin(stations_used)]
        locations_table = self.create_locations_table(stations_subset)
        locations_table.to_csv(study_result_directory / "{}_locations.csv".format(study_id))
        for station_id in stations_used:
            if not stations_table.loc[station_id, "approved"]:
                continue
            station_data = data[data["station_id"] == station_id]
            splits = station_data.shape[0] // MAX_EIM_ROWS + 1
            for batch_no, batch in enumerate(np.array_split(station_data, splits)):
                results_table = self.create_results_table(batch)
                result_file = study_id + "_" + station_id + "_b" + str(batch_no) + ".csv"
                results_table.to_csv(study_result_directory / result_file)

            
    def create_results_table(self, data: pd.DataFrame):
        """ Creates dataframe with required time series result info
        
        Args:
            data: each row is the result from one parameter
        Returns:
            modified data with proper columns and values
        """
        stations_table = pd.read_csv(stations, index_col="station_id")
        data["Study ID"] = data["station_id"].map(stations_table["eim_study_id"])
        data["Study Specific Location ID"] = data["station_id"].map(stations_table["eim_location_study"])
        data["Field Collection Type"] = "Measurement"
        data["Field Collector"] = data["station_id"].map(stations_table["collector"])
        data["Field Collection Reference Point"] = data["station_id"].map(stations_table["reference_point"])
        data["Matrix"] = "Water"
        data["Source"] = "Salt/Marine Water"
        eim_date_format = "%m/%d/%Y"
        eim_time_format = "%H:%M:%S"
        data["Start Date"] = pd.to_datetime(data["datetime"]).dt.strftime(eim_date_format)
        data["Start Time"] = pd.to_datetime(data["datetime"]).dt.strftime(eim_time_format)

        data["parameter"] = data["parameter"].map(parameter_names)
        data["unit"] = data["unit"].map(units)
        results_table = data.rename(columns=results_columns)
        results_table = results_table.loc[:, results_table.columns.isin(
            [
                "Study ID",
                "Instrument ID",
                "Location ID", 
                "Study Specific Location ID",
                "Field Collection Type",
                "Field Collector",
                "Matrix",
                "Source",
                "Start Date",
                "Start Time",
                "Result Parameter Name",
                "Result Value",
                "Result Unit",
                "Result Method",
                "Result Data Qualifier",
                "Field Collection Reference Point",
                "Field Collection Depth",
                "Field Collection Depth Units"
            ]
        )]



        return results_table
        

    def create_locations_table(self, station_data: pd.DataFrame):
        """ Creates dataframe with required station information 
        
        Args:
            station_data: each row is a location 
        Returns:
            modified station data with proper columns and names
        """
        station_data.reset_index(inplace=True)
        location_data = station_data.rename(columns=location_columns)
        location_data["Location Setting"] = "Water"
        location_data["Coordinate System"] = "LAT/LONG"
        # 24 = Discrete Monitoring Point
        location_data["Horizontal Coordinates Represent"] = 24
        location_data = location_data.loc[:, location_data.columns.isin(
            [
                "Location ID",
                "Location Name",
                "Location Setting",
                "Location Description",
                "Coordinate System",
                "Latitude Degrees",
                "Longitude Degrees",
                "Horizontal Coordinates Represent",
                "Horizontal Datum",
                "Horizontal Coordinate Accuracy",
                "Horizontal Coordinate Collection Method"
            ]
        )]
        return location_data
