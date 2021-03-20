import numpy as np
import pandas as pd
from scipy import interpolate

osrm_out = pd.read_csv('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/python/osrm_out.csv')
segments = pd.read_csv('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')

osrm_out["isUsedAug"] = False

arac_list = osrm_out["arac_id"].unique()


def get_arac_osrm(arac, osrm_out, segments):
    index = osrm_out["arac_id"] == arac
    route_list = osrm_out.loc[index, "route_id"].unique()
    out = pd.DataFrame()

    for route_id in route_list:
        route_loc = (osrm_out.loc[index, "route_id"] == route_id) & osrm_out.loc[index, "isMatchedSegments"]
        if route_loc.sum() > 1:
            data = osrm_out[index].loc[
                route_loc, ["arac_id", "raw_time", "route_id", "assos_segment_id", "distance_to_start_node"]]
            data = data.drop_duplicates(subset=["raw_time", "distance_to_start_node"], ignore_index=True)

            if data.shape[0] < 2:
                # raise NotImplementedError
                print(f"arac_id= {arac} route= {route_id} data < 2")
                continue
            if osrm_out[index].loc[route_loc, "assos_dir"].drop_duplicates().shape[0] > 1:
                # raise NotImplementedError
                print(f"arac_id= {arac} unique route ({route_id}) data dir > 1")
                continue

            data = data.sort_values("raw_time")
            first_ii = \
                np.equal(data.iloc[0]["assos_segment_id"].astype('int'), segments["segment_id"].to_numpy()).nonzero()[0]
            last_ii = \
                np.equal(data.iloc[-1]["assos_segment_id"].astype('int'), segments["segment_id"].to_numpy()).nonzero()[
                    0]

            if (first_ii.shape[0] == 0) | (last_ii.shape[0] == 0):
                # raise NotImplementedError
                print(f"arac_id= {arac} undefined route ({route_id}) start (or end)")
                continue
            first_ii = first_ii.item()
            last_ii = last_ii.item()
            segment_list = segments.loc[first_ii:last_ii, "segment_id"]

            space_axis = segments.loc[first_ii:last_ii, "calc_length"]
            space_axis = space_axis.cumsum() - space_axis

            b = np.equal(data["assos_segment_id"].to_numpy()[:, None], segment_list.to_numpy())

            data["data_axis"] = space_axis.iloc[b.argmax(axis=1)].to_numpy() + data["distance_to_start_node"]
            data["raw_time"] = pd.to_datetime(data["raw_time"])
            aux_date = (data["raw_time"] - pd.to_datetime('1900')).dt.total_seconds()
            # try:
            f = interpolate.interp1d(data.data_axis.to_numpy(), aux_date,
                                     kind="linear", bounds_error=False,
                                     fill_value="extrapolate")
            interpolated_time = pd.to_timedelta(f(space_axis.to_numpy()), unit="seconds") + pd.to_datetime('1900')
            # except RuntimeWarning as warn:
            #     print(f"arac_id = {arac}, route_id = {route_id} " + repr(warn))

            aug_data = pd.DataFrame()
            aug_data["segment_id"] = segment_list
            aug_data["aug_time"] = interpolated_time
            aug_data["aug_type"] = 0
            aug_data.loc[b.any(axis=0), "aug_type"] = 1
            aug_data.loc[~b.any(axis=0), "aug_type"] = 2
            aug_data["arac_id"] = arac
            aug_data["route_id"] = route_id
            aug_data["lat"] = segments.loc[first_ii:last_ii, "startLat"]
            aug_data["lon"] = segments.loc[first_ii:last_ii, "startLon"]
            aug_data["dir"] = segments.loc[first_ii:last_ii, "dir"]
            aug_data["speed"] = 1e-3 * np.diff(space_axis, append=np.nan) / (
                    np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h'))
            aug_data["time_diff"] = np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h')
            aug_data["space_diff"] = 1e-3 * np.diff(space_axis, append=np.nan)

            aug_data = aug_data.drop(aug_data.index[0])
            out = pd.concat([out, aug_data], axis=0, ignore_index=True)
    return out


aug_data = pd.DataFrame()

length = len(arac_list)

for i, arac in enumerate(arac_list):
    arac_osrm = get_arac_osrm(arac, osrm_out, segments)
    aug_data = pd.concat([aug_data, arac_osrm], axis=0, ignore_index=True)
    if not i % 500:
        print(f"{i} in {length}, percent = {i / length * 100}")
