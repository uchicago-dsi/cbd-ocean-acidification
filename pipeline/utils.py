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

ceden_params = {
    "salinity": "Salinity",
    "total_alkalinity": "Alkalinity as CaCO3",
    "water_temperature": "Temperature",
    "oxygen_concentration": "Oxygen, Dissolved",
    "oxygen_saturation": "Oxygen, Saturation",
    "co2": "Carbon dioxide, free",
    "water_pressure": "Pressure",
}

ceden_stations = {
    "HIOC_Hogisland1": "201ST1775",
    "NERRS_elkapwq": "",
    "NERRS_elksmwq": "306-ELKHO-33",
    "NERRS_elkvmwq": "306ELKNVM",
    "NERRS_sfbccwq": "CHINA CAMP",
    "NERRS_sfbfmwq": "",
    "NERRS_sfbgcwq": "LLFS17_17",
    "NERRS_sfbsmwq": "",
    "NERRS_tjroswq": "",
    "PMELCO2_cce1": "",
    "PMELCO2_cce2": "",
    "CARLSBD_Aquafarm1": "",
    "cencoos_Carquinez": "",
    "cencoos_Humboldt": "",
    "cencoos_Tiburon": "",
    "cencoos_Trinidad": "",
}

ceden_station_misc = {
    "EventCode": "WQ",  # for for Water Quality
    "ProjectCode": "",
    "ProtocolCode": "Not Recorded",
    "AgencyCode": "Not Recorded",
    "SampleComments": "",
    "LocationCode": "Not Recorded",
    "GeometryShape": "Point",
    "CoordinateNumber": "1",
    "Datum": "NR",
    "CoordinateSource": "NR",
    "Elevation": "",
    "UnitElevation": "",
    "StationDetailVerBy": "",
    "StationDetailVerDate": "",
    "StationDetailComments": "",
}

ceden_field_misc = {}

