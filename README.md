# Automated Ocean Acidification Data Pipeline

Automates retrieval and submission of ocean acidification data for the Center for Biological Diversity.

Currently contains scripts to

- Retrieve and aggregate data from [NERRS](http://cdmo.baruch.sc.edu/), [King County](https://green2.kingcounty.gov/marine-buoy/Data.aspx), [Ocean Observatories Initiative](https://oceanobservatories.org/) and [CeNCOOS](https://www.cencoos.org/)
- Reformat that data to make it ready for submission to California, Washington, and Hawaii.


## Initial Setup

These steps must be taken before using the program. Most will only be required once. 
### Software Setup

This setup should only have to be run once per machine you run it on.

1. Install Docker. The project is designed to run in a Docker container. Therefore, the only prerequisite is Docker: [Get Docker](https://docs.docker.com/get-docker/)

2. Clone the repository. If you haven't already: `git clone https://github.com/11th-Hour-Data-Science/cbd-ocean-acidification.git`

3. Change to the root project directory: `cd cbd-ocean-acidification`

4. Build the Docker image: `docker build --tag cbd .`


### Record Keeping Setup

Some steps in the 303(d) data submission process must be taken manually once before completion. The `metadata/stations.csv` contains metadata about the stations that are available to retrieve data from. You can open this in Excel or any csv editor of your choice. Just be sure to save any changes as a csv. 

#### Washington

Washington uses EIM to handle environmental data. It has three distinct types of data. 
- Results, which are the values of a given parameter at a given
 time and place, are formatted in a results table automatically.
- Locations, which are the descriptions of locations from which results originate, are formatted in a locations table automatically.
- Studies are data about how the results were collected and who administers the locations. These must be submitted manually once.

To set up submitting data to Washington:

1. Follow the instructions [here](https://apps.ecology.wa.gov/eim/help/HelpDocuments/OpenDocument/14) through creating the relevant studies
2. Update `stations.csv` to add the `eim_study_id` to the relevant stations
3. Ensure all stations you wish to submit have the required information in `stations.csv` and `station_parameter_metadata.csv`

For more information, visit the [EIM page](https://ecology.wa.gov/Research-Data/Data-resources/Environmental-Information-Management-database/EIM-submit-data)

#### California

CEDEN is California's primary portal for environmental data upload, but it does not accept time series data as of this writing. All time-series data must be submitted to the [Integrated Report Document Upload Portal](https://www.waterboards.ca.gov/water_issues/programs/water_quality_assessment/ir_upload_portal.html). To submit to California:

1. Create an IR Portal account: https://public2.waterboards.ca.gov/IRPORTAL/Account/Register
2. Ensure all stations you wish to submit have the required information in `stations.csv` and `station_parameter_metadata.csv`

#### Hawaii


#### Stations

For new stations and locations:

1. Contact the data source to receive approval, ensure we are following their terms of service, and to ensure they are not already submitting data. 
2. If the station's data is available through one of the available collectors: King County, IPACOA, ERDDAP, find its ID in this service and use it as our station_id
3. If it is not available through one of the available collectors, a new scraper will need to be created. If you are able you can try to write one yourself (following existing patterns) and open a Pull Request. Otherwise open an [issue](https://github.com/11th-Hour-Data-Science/cbd-ocean-acidification/issues/new) describing the new station you would like and where you retrieved its data from. 
4. Add an entry to `stations.csv` with all relevant data. You may need to contact the source.  
5. Add entries to `station_parameter_metadata.csv` with all relevant data. You may need to contact the source. 

## Usage

### NERRS
If you are submitting NERRS data:
1. Get your ipv4 address (going to a website like https://whatismyipaddress.com/ should do it)
2. Request a webservices account from NERRS: http://cdmo.baruch.sc.edu/web-services-request/
3. Wait for your confirmation email. Since most IP addresses change over time, you may have to do this before each time you acquire NERRS data, or get a static IP. 


1. In the project root directory, run:
   ```sh
    bash run_tool.sh <STATE> <start_date> <end_date>
   ```
   where <STATE> should be the state name (California, Hawaii, or Washington), <start_date> and <end_date> should be dates YYYY/MM/DD format (exclude <>).
   This will prompt your password, as we are using sudo priveleges to change the owner of the output files from root (since docker created them) to the current
   user. 
2. Results will be saved in `results/STATE/YYYY-MM-DDTHH-MM` with a `README.txt` file explaining further instructions. 


### Without Docker (discouraged)

1. In the project root directory, run:
   ```sh
    python main.py <STATE> --start <start_date> --end <end_date>
   ```
   where <STATE> should be the state name (California, Hawaii, or Washington), <start_date> and <end_date> should be dates YYYY/MM/DD format (exclude <>). 
2. Results will be saved in `results/STATE/YYYY-MM-DDTHH-MM` with a `README.txt` file explaining further instructions. 


## Directory Structure

### pipeline/metadata/

- `ipacoa_measurement_lookup.csv`: Lookup table that shows IDs, names, and measurement units for all measurements provided by stations listed in the asset list.
- `ipacoa_platform_measurements.csv`: Contains all combinations of stations and measurements accessible through IPACOA. The `process` column indicates whether that information is going to be downloaded by the scraper `ipacoa.py`. If you want to add additional stations or measurements, you should update `process` column of the relevant row to be `True`. Otherwise that information will not be included in the dataset. Currently only ocean acidification related measurements of West Coast stations are set to have `process=True`.
  <br><br>
- `king-county-keys.json`: Contains necessary keys to make a `GET` request to King County's API. Used by the `kingcounty.py` script.
- `kingcounty_measurement_lookup.csv`: Contains information on measurements, units, and devices used in the stations listed by King County data portal.
  <br><br>
- `stations.csv`: Table containing information on all stations that can be accessed through both IPACOA and King County data sources.

## Contact

You can contact us by opening an issue or emailing tspread at uchicago edu

Project Link: [https://github.com/chicago-cdac/cbd-ocean-acidification]()
