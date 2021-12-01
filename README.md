# Automated Ocean Acidification Data Pipeline

Automates retrieval and submission of ocean acidification data for the Center for Biological Diversity.

Currently contains scripts to

- Retrieve and aggregate data from [IPACOA](https://www.ipacoa.org/) and [King County](https://green2.kingcounty.gov/marine-buoy/Data.aspx).
- Reformat that data to make it ready for [CEDEN](http://ceden.org/index.shtml) submission.

## Prerequisites

The project is designed to run in a Docker container. Therefore, the only prerequisite is Docker: [Get Docker](https://docs.docker.com/get-docker/)

If you want to run the scripts locally in a Python installed environment, then refer to the `requirements.txt` file for needed packages.

## Usage

### Through Docker (recommended)

1. Clone the repo
   ```sh
    git clone https://github.com/11th-Hour-Data-Science/cbd-ocean-acidification.git
   ```
2. Build the Docker image
   ```sh
   docker build --tag cbd .
   ```
3. Run the commands in the `shell.sh` script within the Docker container.
   ```sh
    docker run --name cbd cbd
   ```
4. You can access the output files using the CLI through Docker Desktop.
   <br><br>

### Or locally

1. Install packages
   ```sh
   pip install -r requirements.txt
   ```
2. Allow access
   ```sh
   chmod +x shell.sh
   ```
3. Run the scripts
   ```sh
   ./shell.sh
   ```

## Directory Structure

### pipeline/

- `ipacoa.py`: Python script to get water quality data from [IPACOA](https://www.ipacoa.org/).
- `kingcounty.py`: Python script to get water quality data from [King County](https://green2.kingcounty.gov/marine-buoy/Data.aspx).
- `ceden.py`: Python script to collect water quality data from the `data` folder and populate the [CEDEN](http://ceden.org/index.shtml) `.xls` template under the `templates` folder. The populated templates are stored at `data/submittal`.
- `getdata.py`: Python script to call functions within `kingcounty.py` and `ipacoa.py` and store the concatenated results at `data/measurements.csv`. Change `months=6` to desired value at line 10 to get older/newer data.
- `utils.py`: Contains relevant dictionaries used to normalize column and value names across different sources, as well as to comply with CEDEN template guidelines.

### data/

- `ipacoa/lookups/asset_list.csv`: Contains information on all stations and buoys accessible through IPACOA.
- `ipacoa/lookups/measurement_lookup.csv`: Lookup table that shows IDs, names, and measurement units for all measurements provided by stations listed in the asset list.
- `ipacoa/lookups/platform_measurements.csv`: Contains all combinations of stations and measurements accessible through IPACOA. The `process` column indicates whether that information is going to be downloaded by the scraper `ipacoa.py`. If you want to add additional stations or measurements, you should update `process` column of the relevant row to be `True`. Otherwise that information will not be included in the dataset. Currently only ocean acidification related measurements of West Coast stations are set to have `process=True`.
- `ipacoa/ipacoa_sample.csv`: Sample output of `ipacoa.py`.
  <br><br>
- `king-county/keys/king-county-keys.json`: Contains necessary keys to make a `GET` request to King County's API. Used by the `kingcounty.py` script.
- `king-county/lookups/measurement_lookup.csv`: Contains information on measurements, units, and devices used in the stations listed by King County data portal.
  <br><br>
- `submittal/`: Directory in which filled-in CEDEN templates are exported.
  <br><br>
- `stations.csv`: Table containing information on all stations that can be accessed through both IPACOA and King County data sources.

### templates/

- `ceden_field_template.xls`: Empty CEDEN template to be filled by `ceden.py`.

`.gitignore`: Files to be ignored by git.

`Dockerfile`: Text document that contains the commands to assemble a Docker image.

`requirements.txt`: Contains the Python package requirements with versions. Necessary for Docker to create an image that can run the scripts.

`shell.sh`: Shell script to run the Python files in correct order to assemble templates ready to be submitted.

## Contact

Egemen Pamukcu - [GitHub](github.com/egemenpamukcu) - egemenpamukcu@uchicago.edu

Project Link: [https://github.com/11th-Hour-Data-Science/cbd-ocean-acidification]()
