import collections
import pytest
from datetime import datetime, timedelta

from .ipacoa import IPACOA
from .kingcounty import KingCounty
from .erddap import ERDDAP

class TestDataCollection():

    now = datetime.now()
    month_prior = datetime.now() - timedelta(30)


    def test_ipacoa_default(self):
        station_id = "OSU_CB06"
        collector = IPACOA()
        self.run_collector_tests(collector, station_id, self.month_prior, self.now)

    def test_ooi_default(self):
        station_id = "ooi-ce01issm-rid16-06-phsend000"
        collector = ERDDAP("https://erddap.dataexplorer.oceanobservatories.org/erddap/")
        self.run_collector_tests(collector, station_id, self.month_prior, self.now)

    def test_cencoos_default(self):
        station_id = "tiburon-water-tibc1"
        collector = ERDDAP("https://erddap.cencoos.org/erddap/")
        self.run_collector_tests(collector, station_id, self.month_prior, self.now)
    
    def test_kingcounty_default(self):
        station_id = "POINT_WILLIAMS"
        collector = KingCounty()
        self.run_collector_tests(collector, station_id, self.month_prior, self.now)


    def run_collector_tests(self, collector, station_id, start, end):
        """ Runs get_data tests and asserts properly formed table """
        data = collector.get_data(station_id, start, end)
        expected_columns = {
            "datetime", "latitude", "longitude", "depth", "station_id",
            "parameter", "value", "quality", "unit", "instrument"
        }
        ## depth unit and reference point?
        assert set(data.columns) == expected_columns

        

