# -*- coding: utf-8 -*-

import numpy as np

# column names to be renamed before pivot to long format
positional_column_mapping = {
    'time (UTC)': 'datetime',
    'latitude (degrees_north)': 'latitude',
    'longitude (degrees_east)': 'longitude',
    'station': 'staion_id',
    'z (m)': 'depth',
    'Date': 'datetime',
    'Depth_m': 'depth',
    "level": "depth",
    "utcstamp": "datetime"
}

# parameter names to be renamed after pivot to long format
parameter_dict = {
    "A1_AirTemp": "air_temperature",
    "A1_BarPress": "air_pressure",
    "H1_Pressure": "water_pressure",
    "H1_WaterTemp": "water_temperature",
    "H1_OxygenSat": "oxygen_saturation",
    "H1_Oxygen": "oxygen_concentration",
    "H4_Oxygen": "oxygen_concentration",
    "H1_pH": "pH",
    "H1_AlkalinityTot": "total_alkalinity",
    "H1_Salinity": "salinity",
    "H1_TCO2": "tco2",
    "H1_CO2": "co2",
    "H2_CO2": "co2",
    "Air_Pressure": "air_pressure",
    "Air_Temperature": "air_temperature",
    "Dissolved_Oxygen": "oxygen_concentration",
    "Dissolved_Oxygen_Sat": "oxygen_saturation",
    "Sonde_pH": "pH",
    "SeaFET_External_pH_recalc_w_salinity": "pH_salinity",
    "SeaFET_External_pH_1_recalc_w": "pH_external",
    "Salinity": "salinity",
    "Water_Temperature": "water_temperature",
    "SeaFET_Temperature": "water_temperature",
    "sea_water_practical_salinity": "salinity",
    "sea_water_ph_reported_on_total_scale": "pH",
    "sea_water_ph_reported_on_total_scale_salinity_corrected": "pH_salinity",
    "sea_water_ph_reported_on_total_scale_internal": "pH_internal",
    "sea_water_ph_reported_on_total_scale_external": "pH_external",
    "sea_water_temperature" : "water_temperature",
    "sea_water_pressure": "water_pressure",
    "mass_concentration_of_oxygen_in_sea_water" : "oxygen_concentration",
    "fractional_saturation_of_oxygen_in_sea_water" : "oxygen_saturation",
    "sea_water_electrical_conductivity" : "conductivity",
    "total_dissolved_solids" : "total_dissolved_solids",
    "sea_water_turbidity" : "turbidity",
    "total_alkalinity_ta" : "total_alkalinity",
    "omega_aragonite": "omega_aragonite",
    "do_pct": "oxygen_saturation",
    "do_mgl": "oxygen_concentration",
    "temp": "water_temperature",
    "sal": "salinity",
    "turb": "turbidity",
    "spcond": "conductivity",
    "ph": "pH",
    "co2": "Carbon Dioxide",
}

ceden_station_misc = {
    "EventCode": "WQ",  # for for Water Quality
    "ProjectCode": "CBD-MONITORING-ACID",
    "ProtocolCode": "Not Recorded",
    "AgencyCode": "CBD",
    "SampleComments": "",
    "LocationCode": "Not Recorded",
    "GeometryShape": "Point",
    "CoordinateNumber": "1",
    "CoordinateSource": "NR",
    "Elevation": "",
    "UnitElevation": "",
    "StationDetailVerBy": "",
    "StationDetailVerDate": "",
    "StationDetailComments": "",
}

ceden_field_misc = {
    "ProjectCode": "CBD-MONITORING-ACID",
    "EventCode": "WQ",
    "ProtocolCode": "Not Recorded",
    "SampleComments": "",
    "LocationCode": "Not Recorded",
    "GeometryShape": "Point",
    "CollectionMethodCode": "Water_Grab",
    "PositionWaterColumn": "Not Applicable",
    "FieldCollectionComments": "",
    "FractionName": "Not Recorded",
    "FieldReplicate": "1",
    "ResQualCode": "=",
    "ComplianceCode": "NR",
    "BatchVerificationCode": "NR",
    "CalibrationDate": "01/Jan/1950",
    "FieldResultComments": "",
}

ceden_matrix_dict = {
    "total_alkalinity": "samplewater",
    "pH": "samplewater",
    "salinity": "samplewater",
    "water_temperature": "samplewater",
    "oxygen_concentration": "samplewater",
    "oxygen_saturation": "samplewater",
    "co2": "samplewater",
    "water_pressure": "samplewater",
    "air_temperature": "air",
    "air_pressure": "air",
    "tco2": "samplewater",
}

ceden_unit_dict = {
    "µmol/kg": "umol/g",  # multiply with 1000
    "PSU": "psu",
    "°F": "Deg C",  # convert to celsius
    "mg/L": "mg/L",
    "%": "%",
    "ppm": "mg/L",
    # "inHg": "mmHG",  # divide by 0.0393701, need to validate
    "inHg": "mmHg",
    # "µatm": "per mil",  # not sure, need to validate
    "µatm": "uatm",
    "dbar": "dbar",
    np.NaN: "none",
}

ceden_datum_dict = {
    "Hog Island Oysters": "NR",
    "NERRS ELK": "NAVD88",
    "NERRS SFB": "NAVD88",
    "NERRS TJR": "NAVD88",
    "PMEL-CO2": "NR",
    "Carlsbad Aquafarm": "NR",
    "CeNCOOS": "NR",
}
