import pandas as pd
import kingcounty
import ipacoa
from dateutil.relativedelta import relativedelta
from datetime import date
import os

if __name__ == "__main__":
    PATH = os.path.abspath(__file__)
    six_months_back = (date.today() - relativedelta(months=6)).strftime("%Y-%m-%d")

    # additional scrapers must be added here
    kc = kingcounty.get_data(start_date=six_months_back)
    ip = ipacoa.get_data(start_date=six_months_back)
    measurements = pd.concat([kc, ip], ignore_index=True)

    measurements_path = os.path.abspath(
        os.path.join(PATH, "..", "..", "data", "measurements.csv")
    )

    measurements.to_csv(measurements_path, index=False)
