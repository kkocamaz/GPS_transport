import numpy as np
import pandas as pd
from scipy import interpolate

osrm_out = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/osrm_out.csv')
segments = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')

osrm_out["isUsedAug"] = False

arac_list = osrm_out["arac_id"].unique()

data_list = []

for arac in arac_list:

    index = osrm_out["arac_id"] == arac
    route_list = osrm_out.loc[index, "route_id"].unique()

    for route_id in route_list:
        route_loc = (osrm_out.loc[index, "route_id"] == route_id) & osrm_out.loc[index, "isMatchedSegments"]
        route_index = osrm_out.loc[index].loc[route_loc].index
        if route_index.shape[0] > 1:
            route_data = osrm_out.loc[route_index]
            route_data = route_data.drop_duplicates(subset=["raw_time"], ignore_index=True)
            route_data = route_data.drop_duplicates(subset=["distance_from_start"], ignore_index=True)

            if route_data.shape[0] < 2:
                # raise NotImplementedError
                print(f"arac_id= {arac} route= {route_id} data < 2")
                continue
            if route_data["assos_dir"].drop_duplicates().shape[0] > 1:
                # raise NotImplementedError
                print(f"arac_id= {arac} unique route ({route_id}) data dir > 1")
                continue

            route_data = route_data.sort_values("raw_time")

            first_ii = \
                np.equal(route_data.iloc[0]["assos_segment_id"].astype('int'),
                         segments["segment_id"].to_numpy()).nonzero()[0]
            last_ii = \
                np.equal(route_data.iloc[-1]["assos_segment_id"].astype('int'),
                         segments["segment_id"].to_numpy()).nonzero()[
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

            b = np.equal(route_data["assos_segment_id"].to_numpy()[:, None], segment_list.to_numpy())

            route_data["data_axis"] = space_axis.iloc[b.argmax(axis=1)].to_numpy() + route_data[
                "distance_to_start_node"]
            route_data["raw_time"] = pd.to_datetime(route_data["raw_time"])
            aux_date = (route_data["raw_time"] - pd.to_datetime('1900')).dt.total_seconds()

            f = interpolate.interp1d(route_data["data_axis"].to_numpy(), aux_date,
                                     kind="linear", bounds_error=False,
                                     fill_value="extrapolate")
            interpolated_time = pd.to_timedelta(f(space_axis.to_numpy()), unit="seconds") + pd.to_datetime('1900')

            osrm_out.loc[route_index, "isUsedAug"] = True

            aug_data = pd.DataFrame(
                columns=["segment_id", "aug_time", "aug_type", "arac_id", "route_id", "lat", "lon", "dir"])

            aug_data["segment_id"] = segment_list.to_numpy()
            aug_data["aug_time"] = interpolated_time
            aug_data["aug_type"] = 0
            aug_data.loc[b.any(axis=0), "aug_type"] = 1
            aug_data.loc[~b.any(axis=0), "aug_type"] = 2
            aug_data["arac_id"] = arac
            aug_data["route_id"] = route_id
            aug_data["lat"] = segments.loc[first_ii:last_ii, "startLat"].to_numpy()
            aug_data["lon"] = segments.loc[first_ii:last_ii, "startLon"].to_numpy()
            aug_data["dir"] = segments.loc[first_ii:last_ii, "dir"].to_numpy()
            aug_data["speed"] = 1e-3 * np.diff(space_axis, append=np.nan) / (
                    np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h'))
            aug_data["time_diff"] = np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h')
            aug_data["space_diff"] = 1e-3 * np.diff(space_axis, append=np.nan)

            aug_data = aug_data.drop(aug_data.index[0])

            data_list.append(aug_data)

            # osrm_out.loc[route_index, "aug_segment_id"] = segment_list.to_numpy()[1:]
            # osrm_out.loc[route_index, "aug_time"] = interpolated_time.to_numpy()[1:]
            # osrm_out.loc[route_index, "aug_type"] = 0
            # osrm_out.loc[route_data.loc[b.any(0)[1:]].index, "aug_type"] = 1
            # osrm_out.loc[route_data.loc[~b.any(0)[1:]].index, "aug_type"] = 2

out = pd.concat(data_list)
