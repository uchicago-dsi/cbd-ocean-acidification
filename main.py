import argparse
from datetime import datetime, timedelta
import logging
from re import I
from requests.exceptions import HTTPError
import pandas as pd
from pathlib import Path

from pipeline.erddap import ERDDAP
from pipeline.ipacoa import IPACOA
from pipeline.kingcounty import KingCounty
from pipeline.eim import EIM
from pipeline.ceden import CEDEN
from pipeline.nerrs import NERRS
from pipeline.hawaii import Hawaii
from pipeline.oregon import Oregon

HERE = Path(__file__).resolve().parent
STATIONS = HERE / 'pipeline' / 'metadata' / 'stations.csv'

collectors = {
    "NERRS": NERRS(),
    "OOI": ERDDAP("https://erddap.dataexplorer.oceanobservatories.org/erddap/"),
    "CeNCOOS": ERDDAP("https://erddap.cencoos.org/erddap/"),
    "King County": KingCounty(),
    "IPACOA": IPACOA(),
}

formatters = {
    "Washington": EIM,
    "California": CEDEN,
    "Hawaii": Hawaii,
    "Oregon": Oregon,
}

def collect_data(state, start_time, end_time):
    """ Collects all data from state in time period 
    
    Args:
        state (str): One of 'California', 'Washington', or 'Hawaii'
            All stations in stations.csv from this state will be queried
            for the input time period. 
        start_time (datetime):  earliest date from which to collect
        end_time (datetime):  latest date from which to collect 
    Returns:
        data (pd.DataFrame): Table containing all data points
    """
    stations = pd.read_csv(STATIONS, index_col="station_id")
    state_stations = stations[stations['state'] == state]
    all_station_data = []
    for index, row in state_stations.iterrows():
        logging.info(f"Collecting data from {index}")
        if row["provider"] == "Test":
            continue
        try:
            collector = collectors[row["provider"]]
            station_data = collector.get_data(index, start_time, end_time)
            logging.info(f"Collected {len(station_data)} rows from {index}")
            all_station_data.append(station_data)
        except HTTPError as e:
            logging.warning(e)
        except KeyError as e:
            logging.warning(f"{row['provider']} collector not implemented")
            logging.info(e, exc_info=True)
    data = pd.concat(all_station_data)
    return data

def format_data(state, data, output_directory):
    """ Formats input data according to state's specifications
    
    Args:
        state (str): One of 'California', 'Washington', or 'Hawaii'
        data (pd.DataFrame): Table containing relevant observations
    Returns:
        Nothing. Saves relevant documents to folder with name {state}-{unixtime}
    """
    formatter = formatters[state](output_directory)
    formatter.format_data_for_agency(data)
    

if __name__ == "__main__":
    # set up for command line arguments
    parser = argparse.ArgumentParser(
        description="Automated oceanographic data collection for 303(d) reviews"
    )
    parser.add_argument("state", metavar="STATE", type=str,
        help="State from which to gather and prepare data"
    )
    parser.add_argument("--start", type=str, default=None,
        help="YYYY/MM/DD. Earliest time from which to gather data. Default 30 days ago."
    )
    parser.add_argument("--end", type=str,
        help="YYYY/MM/DD. Latest time from which to gather data. Default today.")
    args = parser.parse_args()
    # set defaults
    if args.start == None:
        args.start = datetime.now() - timedelta(30)
    else:
        args.start = datetime.strptime(args.start, "%Y/%m/%d")
    if args.end == None:
        args.end = datetime.now()
    else:
        args.end = datetime.strptime(args.end, "%Y/%m/%d")
    # set up paths
    request_time = datetime.now().strftime("%Y-%m-%dT%H-%M")
    results_directory = HERE / "output" / args.state / request_time
    results_directory.mkdir(exist_ok=True, parents=True)
    logfile = results_directory / "output.log"
    # set up logging
    logging.basicConfig(
        filename=logfile , encoding='utf-8', level=logging.INFO,
        format='%(levelno)s %(asctime)s %(pathname)s %(message)s'
    )
    # run pipeline
    logging.info(
        f"Collecting data for {args.state} from {args.start} to {args.end}"
    )
    data = collect_data(args.state, args.start, args.end)
    logging.info(
        f"{len(data)} rows of data collected. Formatting for agency..."
    )
    format_data(args.state, data, output_directory=results_directory)
    logging.info("COMPLETE")