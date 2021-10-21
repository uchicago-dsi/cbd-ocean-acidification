import pandas as pd
import numpy as np
from erddapy import ERDDAP

#Retrives data from "CeNCOOS in situ water quality monitoring using the seawater input for Moss
#Landing Marine Laboratory"
def mlml_auto_retrieval(y1, y2):
    e = ERDDAP(
        server="https://erddap.cencoos.org/erddap/",
        protocol="tabledap",
    )

    e.response = "csv"
    e.dataset_id = "mlml_mlml_sea"
    e.constraints = {
        "time>=": "{}".format(y1),
        "time<=": "{}".format(y2),
    }
    
    return e.to_pandas()

#Retrieves data from "CeNCOOS in situ water quality monitoring at Morro bay"
def morobay_auto_retrieval(y1, y2):
    e = ERDDAP(
        server="https://erddap.cencoos.org/erddap/",
        protocol="tabledap",
    )

    e.response = "csv"
    e.dataset_id = "edu_calpoly_marine_morro"
    e.constraints = {
        "time>=": "{}".format(y1),
        "time<=": "{}".format(y2),
    }
    
    return e.to_pandas()    
#Retrieves data from "CeNCOOS in situ water quality monitoring at Humboldt Bay Pier"
def humboldt_auto_retrieval(y1, y2):
    e = ERDDAP(
        server="https://erddap.cencoos.org/erddap/",
        protocol="tabledap",
    )

    e.response = "csv"
    e.dataset_id = "edu_humboldt_humboldt"
    e.constraints = {
        "time>=": "{}".format(y1),
        "time<=": "{}".format(y2),
    }
    
    return e.to_pandas()   



#Retrieves data from "Coastal Endurance: Oregon Inshore Surface Mooring: Near Surface Instrument
#Frame: Seawater pH "
def ceo_auto_retrieval(y1, y2):
    e = ERDDAP(
        server="https://erddap.dataexplorer.oceanobservatories.org/erddap/",
        protocol="tabledap",
    )

    e.response = "csv"
    e.dataset_id = "ooi-ce01issm-rid16-06-phsend000"
    e.constraints = {
        "time>=": "{}".format(y1),
        "time<=": "{}".format(y2),
    }
    
    return e.to_pandas()    



#minimum origin of 2010-09-03T17:11:59Z	

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


#when finalizing I will alter df directly instead of making a copy 
#this is purely for testing purposes
def format_dfs(df):
    df_copy = df.copy()
    df_copy.melt(id_vars= ["time (UTC)", "latitude (degrees_north)",
"longitude (degrees_east)", "z (m)"])
    return df_copy
    


