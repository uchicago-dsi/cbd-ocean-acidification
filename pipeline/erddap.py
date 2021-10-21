import pandas as pd
import numpy as np
from erddapy import ERDDAP

def erdapp_auto_retrival(y1, y2, dataset_id):
    if dataset_id == "ooi-ce01issm-rid16-06-phsend000":
        server = "https://erddap.dataexplorer.oceanobservatories.org/erddap/"
    else:
        server = "https://erddap.cencoos.org/erddap/"
    
    e = ERDDAP(
        server=server,
        protocol="tabledap",
    )

    e.response = "csv"
    e.dataset_id = dataset_id
    e.constraints = {
        "time>=": "{}".format(y1),
        "time<=": "{}".format(y2),
    }
    
    return e.to_pandas()
#will edit df directly once finalized, just editing copy for now for testing purposes

def format_df(df):
    df_copy = df.copy()
    df_copy.melt(id_vars= ["time (UTC)", "latitude (degrees_north)",
"longitude (degrees_east)", "z (m)"])

