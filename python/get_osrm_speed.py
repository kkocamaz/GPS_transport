import numpy as np
import pandas as pd

aug_data = pd.read_csv('python_aug.csv')
osrm_out = pd.read_csv('python_osrm_out.csv')

osrm_out = osrm_out[osrm_out["isUsedAug"]]

osrm_out = osrm_out.reset_index(drop=True)

osrm_out["raw_time"] = pd.to_datetime(osrm_out["raw_time"], format='%d-%b-%Y %H:%M:%S')

osrm_out["space_distance"] = np.nan
osrm_out["time_distance"] = np.nan
osrm_out["speed"] = np.nan

arac_list = osrm_out["arac_id"].unique()

for arac in arac_list:
    route_list = osrm_out.loc[osrm_out["arac_id"] == arac, "route_id"].unique()
    for route in route_list:
        index = (osrm_out["arac_id"] == arac) & (osrm_out["route_id"] == route)
        osrm_out.loc[index, "space_distance"] = 1e-3 * np.diff(osrm_out.loc[index, "distance_from_start"], append=np.nan)
        osrm_out.loc[index, "time_distance"] = np.diff(osrm_out.loc[index, "raw_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h')

osrm_out["speed"] = osrm_out["space_distance"] / osrm_out["time_distance"]

