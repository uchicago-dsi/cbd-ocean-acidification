from .formatter import Formatter
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
stations = HERE / "metadata" / "stations.csv"

MAX_BATCH_SIZE = 150000

location_columns = {
    "provider": "accessed_via",
    "horizontal_coordinate_collection": "horizontal_coordinate_collection_method"
}

results_columns = {
    "station_id": "Station",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "parameter": "Parameter",
    "value": "Value",
    "unit": "Unit",
    "instrument": "Instrument",
    "quality": "QualityCodes",
    "method": "CollectionMethod",
    "depth": "Depth",
    "depth_unit": "DepthUnit"
}

class Hawaii(Formatter):
    state = "Hawaii"
    instructions = """Hawaii Submission Instructions
    Before you run the pipeline, you should have:
     - Filled out the Data submission form: https://health.hawaii.gov/cwb/files/2021/03/data-submittal-2022.pdf
     - Ensure all stations you wish to submit have the required information in `stations.csv` and `station_parameter_metadata.csv`
    After running the pipeline:
     - Results should be saved here: {}
     - Submit results to the HIDOH as CSVs via email: cleanwaterbranch@doh.hawaii.gov
    """  

    def format_data_for_agency(self, data: pd.DataFrame) -> Path:
        split_n = data.shape[0] // MAX_BATCH_SIZE + 1
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
            f.write(self.instructions.format(self.relative_path))

        return self.relative_path

    def populate_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.reset_index()
        df.rename(columns=location_columns, inplace=True,
        errors='ignore')
        df = df.loc[:, df.columns.isin(
            [
                "station_id",
                "name",
                "source"
                "accessed_via",
                "latitude",
                "longitude",
                "description",
                "setting",
                "horizontal_datum",
                "horizontal_coordinate_collection_method",
                "horizontal_coordinate_accuracy",      
            ]
        )]
        return df

    def populate_field_results(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Time"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%H:%M")
        df["Date"] = pd.to_datetime(df["datetime"], utc=True).dt.strftime("%d/%m/%Y")
        df.rename(columns=results_columns, inplace=True, errors="ignore")
        required_results_columns = {
            "Station", "Date", "Time", "Latitude", "Longitude", "Parameter",
            "Value", "Unit", "CollectionMethod", "Instrument", "QualityCodes",
            "Depth", "DepthUnit"
        }
        df = df.loc[:, df.columns.isin(required_results_columns)]
        return df
