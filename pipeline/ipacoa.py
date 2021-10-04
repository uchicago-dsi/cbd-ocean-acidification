import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import time
import os

PLATFORM_URL = 'http://www.ipacoa.org/ssa/get_platform_data.php'
PLATFORMS_PATH = os.path.join('..', 'data', 'ipacoa', 'lookups', 'platform_measurements.csv')

def get_historical_data(path=PLATFORMS_PATH, url=PLATFORM_URL):
	'''
	Queries IPACOA to get information on various environmental measurements. 

	Inputs:
		path (str): Relative path directing to the location of a table containing
			all platform-measurement combinations to query. 
		url (str): IPACOA URL for requesting historical data from platforms. 
	Output:
		Pandas DataFrame: Contains information on all platforms listed in the input csv.
	'''

	platform_measurement = pd.read_csv(PLATFORMS_PATH)
	dfs = []
	for i, (platform, measurement) in tqdm(platform_measurement.iterrows(), 
										   total=platform_measurement.shape[0]):
		params = (
			('platform_id', platform),
			('var_id', measurement),
			('data_type', 'csv'),
		)
		response = requests.get(PLATFORM_URL, params=params)
		
		# Raise error if request is not successful
		response.raise_for_status()

		if response.text == '': 
			continue
		df = pd.read_csv(StringIO(response.text))
		df['platform_id'] = platform
		df['value'] = df.pop(df.columns[2])
		df['measurement_id'] = measurement
		df.rename(columns={' Depth (Ft)': 'depth_ft',
						  'Date and Time': 'date_time'},
				 inplace=True)
		df['depth_ft'] = df['depth_ft'].str.strip(' ft').astype(int)
		df = df[['date_time', 'platform_id', 'measurement_id', 'depth_ft', 'value']]
		dfs.append(df)
		
	all_measures = pd.concat(dfs)
	return all_measures

if __name__ == "__main__":
	df_all = get_historical_data()
	path = os.path.join('..', 'data', 'ipacoa',
		'ipacoa_data_{}.csv'.format(str(int(time.time()))))
	df_all.to_csv(path, index=False)


