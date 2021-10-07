import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import os
import json
from datetime import datetime
import time


def get_all_data(start_date):
    '''
    Queries King County to get environmental measurements from Dockton, Point Williams, 
    Seattle Aquarium, and Quartermaster Yacht Club through a POST request. 

    Input:
        start_date (str): The start date for data in 'MM/DD/YYYY' format. 
    Output:
        Pandas DataFrame: Contains information on all platforms listed in the input csv.
    '''
    if not re.match(r'\d{2}/\d{2}/\d{4}', start_date):
        raise TypeError('Wrong format for start date, format must be MM/DD/YYYY.')


    url = 'https://green2.kingcounty.gov/marine-buoy/Data.aspx'
    
    # Setting up the parameters for POST request
    path = os.path.join('..', 'data', 'king-county', 'keys', 'king-county-keys.json')
    with open(path) as f:
        params = json.load(f)
    
    start_date_key = 'ctl00$kcMasterPagePlaceHolder$startDate'
    end_date_key = 'ctl00$kcMasterPagePlaceHolder$endDate'
    current_time = datetime.now()
    current_date = current_time.strftime('%m/%d/%Y')
    
    dfs = []
    for buoy, data in tqdm(params.items()):
        data[start_date_key] = start_date
        data[end_date_key] = current_date
        response = requests.post(url, data=data)
        tsv = response.text.split('***END***')[1]
        df = pd.read_csv(StringIO(tsv), sep='\t', low_memory=False)
        df['STATION_NAME'] = buoy
        df.dropna(how='all', axis=1, inplace=True)
        col_renames = {c: 'Measure_' + c for c in df.columns if not 
                      ((c.startswith('Qual')) | (c == 'Date') | (c == 'STATION_NAME'))}
        df.rename(columns = col_renames, inplace=True)
        dfs.append(df)
    return(pd.concat(dfs))


if __name__ == '__main__':
	df = get_all_data(input('Enter beginning date in format MM/DD/YYYY:'))
	path = os.path.join('..', 'data', 'king-county',
		'king_county_data_{}.csv'.format(str(int(time.time()))))
	df.to_csv(path, index=False)
