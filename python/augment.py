import numpy as np
import pandas as pd


osrm_out = pd.read_csv('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/python/osrm_out.csv')
segments = pd.read_csv('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')

osrm_out["isUsedAug"] = False

arac_list = osrm_out["arac_id"].unique()

#for arac
arac = arac_list[0]

index = osrm_out["arac_id"] == arac

route_list = osrm_out.loc[index, "route_id"].unique()
n_route = route_list.shape[0]

#for route

route_id = route_list[0]

route_loc = (osrm_out.loc[index, "route_id"] == route_id) & osrm_out.loc[index, "isMatchedSegments"]
if route_loc.sum() > 1:
    data = osrm_out[index].loc[route_loc, ["arac_id", "raw_time", "route_id", "assos_segment_id", "distance_to_start_node"]]
    data = data.drop_duplicates(subset=["raw_time", "distance_to_start_node"], ignore_index=True)

    if data.shape[0] < 2:
        raise NotImplementedError
        # break
    if osrm_out[index].loc[route_loc, "assos_dir"].drop_duplicates().shape[0] > 1:
        raise NotImplementedError
        # break

    data = data.sort_values("raw_time")
    first_ii = np.equal(data.iloc[0]["assos_segment_id"].astype('int'), segments["segment_id"].to_numpy()).nonzero()[0]
    last_ii = np.equal(data.iloc[-1]["assos_segment_id"].astype('int'), segments["segment_id"].to_numpy()).nonzero()[0]

    if (first_ii.shape[0] == 0) | (last_ii.shape[0] == 0):
        raise NotImplementedError
        # break
    first_ii = int(first_ii)
    last_ii = int(last_ii)
    segment_list = segments.loc[first_ii:last_ii, "segment_id"]

    space_axis = segments.loc[first_ii:last_ii, "calc_length"]
    space_axis = space_axis.cumsum() - space_axis

    b = np.equal(data["assos_segment_id"].to_numpy()[:, None], segment_list.to_numpy()).any(0).nonzero()

    data["data_axis"] = space_axis.iloc[b].to_numpy() + data["distance_to_start_node"]
    data["raw_time"] = pd.to_datetime(data["raw_time"])
    aux_date = pd.to_datetime('1990')
