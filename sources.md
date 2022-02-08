# Oceanographic Data Source Documentation

## NOAA NERRS
The National Oceanic and Atmospheric Administration's (NOAA) National Estaurine Research Reserve System (NERRS) contains many sensors on the US west coast that collect time series acidification data. 

Through correspondance, data may be submitted to state agencies, but must follow several guidelines, included in the [manual](http://cdmo.baruch.sc.edu/request-manuals-admin/pdfs/CDMOManualv6.6.pdf). Data should not be held and redistributed after 3 months, QAQC flags must be included, and sources should be cited. Data goes through one round of review quarterly and one round yearly which must be submitted for review by March 15 of the following year. According to the manual "After the CDMO performs the final tertiary QAQC, the data will be posted as authoritative." 

To retrieve data with full QAQC results, a [webservices](https://cdmo.baruch.sc.edu/web-services-request/) acount connected to a static IP must be used. 

## King County

King County Washington has Ocean Acidification monitoring sensors in Puget Sound. They have a slightly outdated [work plan](https://your.kingcounty.gov/dnrp/library/2015/kcr2661.pdf) and communicated through email that they hope to updated Sampling and Analysis Plans for all Mooring and Ocean Acidification Programs by the end of 2022. 

## Ocean Observatories Initiative
[ERDDAP](https://erddap.dataexplorer.oceanobservatories.org/erddap/search/advanced.html?page=1&itemsPerPage=1000&searchFor=&protocol=%28ANY%29&cdm_data_type=%28ANY%29&institution=%28ANY%29&ioos_category=%28ANY%29&keywords=%28ANY%29&long_name=%28ANY%29&standard_name=%28ANY%29&variableName=sea_water_ph_reported_on_total_scale&maxLat=50.0&minLon=-134.0&maxLon=-117.0&minLat=32.0&minTime=&maxTime=). 

[pH sensor specs](https://oceanobservatories.org/wp-content/uploads/2015/10/1341-00510_Data_Product_Spec_PHWATER_OOI.pdf)
[ooipy](https://ooipy.readthedocs.io/en/latest/request.html)

## CeNCOOS
The Central and Northern California Ocean Observing System (CeNCOOS) provides a collection of datasets available through [ERDDAP](https://erddap.cencoos.org/erddap/search/advanced.html?page=1&itemsPerPage=1000&searchFor=&protocol=%28ANY%29&cdm_data_type=%28ANY%29&institution=%28ANY%29&ioos_category=%28ANY%29&keywords=%28ANY%29&long_name=%28ANY%29&standard_name=%28ANY%29&variableName=sea_water_ph_reported_on_total_scale&maxLat=50&minLon=-134&maxLon=-117&minLat=32.0&minTime=&maxTime=). 

### Humboldt State University
Contacted with no response. 

### Moss Landing Marine Laboratory
Contacted with no response.

### Romberg Tiburon Center, San Francisco State University

Depth: Distance the sensors are below the water's surface. The sensors are in a fixed position attached to a pier, so depth also measures tidal range. (units = meters or feet)

Sensor: YSI 6600v2
Website: https://coastalobservations.sfsu.edu/tiburon/#details
email: knielsen@sfsu.edu
License: These data may be used and redistributed for free but they are not intended for legal use, since they may contain inaccuracies. For use for publications please reference the Central and Northern California Ocean Observing system (CeNCOOS) and NOAA. Neither the data provider, CeNCOOS, NOAA, nor the United States Government, nor any of their employees or contractors, makes any warranty, express or implied, including warranties of merchantability and fitness for a particular purpose, or assumes any legal liability for the accuracy, completeness, or usefulness, or this information.

### University of California, Santa Cruz

Depth: ?
Sensor: YSI sonde
Website: http://oceandatacenter.ucsc.edu/SCOOP/about.html
email: kudela@ucse.edu
License:

### San Francisco State University and the California Maritime Academy

Depth: Distance the sensors are below the water's surface. The sensors are in a fixed position attached to a pier, so depth also measures tidal range. (units = meters or feet)
Sensor: YSI 6600v2
Website: https://coastalobservations.sfsu.edu/carquinez

### USGS National Water Information System

Data returned from query from this source is not oceanic and can be discarded.

### Hydrometeorological Automated Data System

Data returned from query from this source is not oceanic and can be discarded.

### Monterey Bay Acquarium

email: ekingsley@mbayaq.org

### Humboldt Bay Burkeolator

email: cencoos_communications@mbari.org

