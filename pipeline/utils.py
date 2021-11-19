# -*- coding: utf-8 -*-

import numpy as np

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
    "SeaFET_External_pH_recalc_w_salinity": "pH",
    "Salinity": "salinity",
    "Water_Temperature": "water_temperature",
    "SeaFET_Temperature": "water_temperature",
}

kc_units = {
    "air_pressure": "inHg",
    "air_temperature": "°F",
    "oxygen_concentration": "mg/L",
    "oxygen_saturation": "%",
    "salinity": "PSU",
    "water_temperature": "°C",
}

kc_devices = {
    "depth": "Sea-Bird HydroCAT-EP datasonde",
    "Air_Temperature": "Vaisala WXT510 meteorological station",
    "Dissolved_Oxygen": "YSI 6600 V2 datasonde",
    "Dissolved_Oxygen_Sat": "YSI 6600 V2 datasonde",
    "Sonde_pH": "Sea-Bird HydroCAT-EP datasonde",
    "SeaFET_External_pH_recalc_w_salinity": "Satlantic SeaFET Sensor",
    "Salinity": "Sea-Bird HydroCAT-EP datasonde",
    "Water_Temperature": "Sea-Bird HydroCAT-EP datasonde",
    "SeaFET_Temperature": "Satlantic SeaFET Sensor",
}

ceden_stations = {
    "HIOC_Hogisland1": "201ST1775",
    "NERRS_elkapwq": "NERRS_elkapwq",
    "NERRS_elksmwq": "306-ELKHO-33",
    "NERRS_elkvmwq": "306ELKNVM",
    "NERRS_sfbccwq": "CHINA CAMP",
    "NERRS_sfbfmwq": "NERRS_sfbfmwq",
    "NERRS_sfbgcwq": "LLFS17_17",
    "NERRS_sfbsmwq": "NERRS_sfbsmwq",
    "NERRS_tjroswq": "NERRS_tjroswq",
    "PMELCO2_cce1": "PMELCO2_cce1",
    "PMELCO2_cce2": "PMELCO2_cce2",
    "CARLSBD_Aquafarm1": "CARLSBD_Aquafarm1",
    "cencoos_Carquinez": "cencoos_Carquinez",
    "cencoos_Humboldt": "cencoos_Humboldt",
    "cencoos_Tiburon": "cencoos_Tiburon",
    "cencoos_Trinidad": "cencoos_Trinidad",
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
    "AgencyCode": "CBD",
    "SampleComments": "",
    "LocationCode": "Not Recorded",
    "GeometryShape": "Point",
    "CollectionMethodCode": "Water_Grab",
    "CollectionDeviceName": "Not Recorded",
    "PositionWaterColumn": "Not Applicable",
    "FieldCollectionComments": "",
    "MethodName": "FieldMeasure",
    "FractionName": "Not Recorded",
    "FieldReplicate": "1",
    "ResQualCode": "=",
    "QACode": "None",
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

ceden_param_dict = {
    "salinity": "Salinity",
    "total_alkalinity": "Alkalinity as CaCO3",
    "water_temperature": "Temperature",
    "oxygen_concentration": "Oxygen, Dissolved",
    "oxygen_saturation": "Oxygen, Saturation",
    "co2": "Carbon dioxide, free",
    "water_pressure": "Pressure",
    "air_pressure": "Barometric Pressure",
    "air_temperature": "Temperature",  # looks like same as water
    "tco2": "Carbon dioxide, free",
    "pH": "pH",
}

ceden_unit_dict = {
    "µmol/kg": "umol/g",  # multiply with 1000
    "PSU": "psu",
    "°F": "Deg C",  # convert to celsius
    "mg/L": "mg/L",
    "%": "%",
    "ppm": "mg/L",
    # "inHg": "mmHG",  # divide by 0.0393701, need to validate
    "inHg": "inHg",
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
