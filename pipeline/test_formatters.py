import collections
import pytest
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

from .ipacoa import IPACOA
from .kingcounty import KingCounty
from .erddap import ERDDAP

from .eim import EIM
from .ceden import CEDEN


#TODO: update nerrs, ipacoa. Test ceden, eim, hawaii

MAX_EIM_BATCH_SIZE = 150000
HERE = Path(__file__).resolve().parent


@pytest.fixture
def small_dataset():
    return pd.read_csv(HERE / "metadata" / "small_dataset.csv", index_col=0)

@pytest.fixture
def state_test(small_dataset, request):
    marker = request.node.get_closest_marker("state_test_data")
    state = marker.args[0]
    small_dataset["station_id"] = "test-{}".format(state)
    return small_dataset



class TestDataCollection():

    now = datetime.now()
    month_prior = datetime.now() - timedelta(30)

    @pytest.mark.state_test_data("ceden")
    def test_ceden_standard(self, state_test):
        formatter = CEDEN()
        results_directory = formatter.format_data_for_agency(state_test)
        ## should have results, locations, and README.txt
        for obj in results_directory.iterdir():
            if "results" in obj.name:
                results = pd.read_csv(obj, index_col=0)
            elif "locations" in obj.name:
                locations = pd.read_csv(obj, index_col=0)
            else:
                assert obj.name == "README.txt"
        self.ceden_tests(results, locations)

    @pytest.mark.state_test_data("eim")
    def test_eim_standard(self, state_test):
        formatter = EIM()
        results_directory = formatter.format_data_for_agency(state_test)
        for obj in results_directory.iterdir():
            if obj.is_file():
                assert obj.name == "README.txt"
            if obj.is_dir():
                study_name = obj.name
                # study information in directory
                location_files_found = 0
                results_batches = []
                for grandchild in obj.iterdir():
                    if "locations" in grandchild.name:
                        location_files_found += 1
                        locations = pd.read_csv(grandchild, index_col=0)
                    else:
                        assert grandchild.name.startswith(study_name)
                        results_batch = pd.read_csv(grandchild, index_col=0)
                        results_batches.append(results_batch)
                assert location_files_found == 1
                results = pd.concat(results_batches)
                self.eim_tests(results, locations)

    @pytest.mark.state_test_data("hawaii")
    def test_hawaii_standard(self, state_test):
        formatter = None



    def eim_tests(self, results: pd.DataFrame, locations: pd.DataFrame):
        """ Runs get_data tests and asserts properly formed table """

        required_results_columns = {
            "Study ID", "Instrument ID", "Location ID", 
            "Study Specific Location ID", "Field Collection Type",
            "Field Collector", "Matrix", "Source", "Start Date",
            "Start Time", "Result Parameter Name", "Result Value",
            "Result Unit", "Result Method"
        }
        optional_results_columns = {
            "Result Data Qualifier", "Field Collection Reference Point",
            "Field Collection Depth", "Field Collection Depth Units"
        }
        ## data has all required columns
        results_columns = set(results.columns)
        assert required_results_columns.issubset(results_columns)
        # data has no additional columns
        assert required_results_columns.union(optional_results_columns).issuperset(results_columns)
        assert results.size < MAX_EIM_BATCH_SIZE

        required_locations_columns = {
            "Location ID", "Location Name", "Location Setting",
            "Location Description", "Coordinate System", "Latitude Degrees", "Longitude Degrees",
            "Horizontal Coordinates Represent", "Horizontal Datum", "Horizontal Coordinate Accuracy",
            "Horizontal Datum Collection Method"
        }
        assert set(locations.columns) == required_locations_columns
        assert set(results["Location ID"].unique()) == set(locations.index)


    def ceden_tests(self, results: pd.DataFrame, locations: pd.DataFrame):

        required_results_columns = {
            "StationCode", "SampleDate", "ProjectCode",
            "CollectionTime", "CollectionMethodCode", "CollectionDeviceName",
            "CollectionDepth", "UnitCollectionDepth", "MatrixName",
            "MethodName", "AnalyteName", "FractionName", "UnitName",
            "Result", "ResQualCode", "QACode"
        }
        required_location_columns = {
            "StationCode", "ProjectCode", "ActualLatitude",
            "ActualLongitude", "Datum", "AgencyCode"

        }
        ## data has all required columns
        results_columns = set(results.columns)
        location_columns = set(locations.columns)
        assert required_results_columns.issubset(results_columns)
        # data has no additional columns
        assert required_location_columns.issubset(location_columns)
        

    def hawaii_tests(self, results: pd.DataFrame, locations: pd.DataFrame):
        required_results_columns = {
            "Station", "Date", "Time", "Latitude", "Longitude", "Parameter",
            "Value", "Unit", "Method", "Instrument", "QualityCodes"
        }


