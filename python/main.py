import numpy as np
import pandas as pd

data = pd.read_json('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/matches.json')
segments = pd.read_csv('C:/Users/Korhan/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')

CONFIDENCE_LEVEL = 0.7

out = pd.DataFrame(columns=pd.Index(['arac_id', 'lon', 'lat', 'raw_time', 'route_id', 'confidence',
                                     'assos_nodes_start', 'assos_nodes_end', 'assos_dir', 'assos_segment_id',
                                     'isMatchedSegments', 'distance_to_start_node', 'distance_to_end_node',
                                     'distance_from_start'],
                                    dtype='object'))


def get_distance(arg1, arg2, mode=1):
    """


    Parameters
    ----------
    arg1 :  [:,1]  lat
            [:,1]  lon
    arg2 : TYPE
        DESCRIPTION.
    mode :  1 = distance between row to row = output shape n,
            2 = distance between row to all rows = output shape n,n

    Returns
    -------
    None.

    """
    return 1e3 * 2. * 6371.393 * np.arcsin(np.sqrt(
        (np.sin(np.deg2rad((arg2[:, 0] - arg1[:, 0]) / 2))) ** 2
        + np.cos(np.deg2rad(arg1[:, 0])) * np.cos(np.deg2rad(arg2[:, 0]))
        * (np.sin(np.deg2rad((arg2[:, 1] - arg1[:, 1]) / 2))) ** 2
    ))


def ismember(arg1, arg2):
    # flags = np.zeros((arg1.shape[0], arg2.shape[0]), dtype='bool')
    # i=11
    # for i in range(arg1.shape[0]):
    #     for j in range(arg2.shape[0]):
    #         flags[i][j] = (arg1[i] == arg2[j]).sum() == 2

    # flags = np.array([[(arg1[i] == arg2[j]).sum() == 2 for j in range(arg2.shape[0])] for i in range(arg1.shape[0])])
    # return flags.nonzero()[0], flags.nonzero()[1]
    aux = np.equal(arg1[:, None, :], arg2[None, :, :]).all(axis=-1).nonzero()
    return aux[0], aux[1]
    # def ismember(arr1, arr2):
    #
    #     out1 = np.zeros_like(arr1, dtype='bool')
    #     for i in range(arr1.shape[-1]):
    #         out1[:, i] = np.in1d(arr1[:, i], arr2[:, i])
    #
    #     out1 = np.logical_and.reduce(out1, axis=1)
    #
    #     out2 = (arr2[:, None] == arr1[out1]).argmax(axis=0)
    #
    #     if not (out2[:, 0] == out2[:, 1]).all():
    #         raise NotImplementedError('problem in ismember')
    #
    #     return out1, out2[:, 0]


for i in range(data.shape[0]):
    # i = 11
    arac_id = data.loc[i, "vehicle"]

    tracepoints = [x["location"] for x in data.loc[i].match_result["tracepoints"] if x is not None]
    tarih = pd.to_datetime([x["tarih"] for x in data.loc[i].match_result["tracepoints"] if x is not None])
    matching_index = [x["matchings_index"] for x in data.loc[i].match_result["tracepoints"] if x is not None]
    confidence = np.array([x["confidence"] for x in data.loc[i]["match_result"]["matchings"]])

    n_data = len(tracepoints)

    osrm_out = pd.DataFrame(tracepoints, columns=["lon", "lat"])

    osrm_out.insert(0, "arac_id", arac_id)

    osrm_out["raw_time"] = tarih

    osrm_out["route_id"] = matching_index
    osrm_out["confidence"] = confidence[matching_index]

    nodes = []
    for leg in data.loc[i]["match_result"]["matchings"]:
        for point in leg["legs"]:
            nodes.append(point["annotation"]["nodes"])
        nodes.append(point["annotation"]["nodes"][-2:])  # for the last point

    osrm_out["assos_nodes_start"] = [x[0] for x in nodes]
    osrm_out["assos_nodes_end"] = [x[1] for x in nodes]

    loc1, loc2 = ismember(osrm_out[["assos_nodes_start", "assos_nodes_end"]].to_numpy(),
                          segments[["start_node", "end_node"]].to_numpy())

    osrm_out["assos_dir"] = np.nan
    osrm_out.loc[loc1, "assos_dir"] = segments.loc[loc2, "dir"].values

    osrm_out["assos_segment_id"] = np.nan
    osrm_out["assos_segment_id"] = osrm_out["assos_segment_id"].astype('Int64')
    osrm_out.loc[loc1, "assos_segment_id"] = segments.loc[loc2, "segment_id"].values

    osrm_out["isMatchedSegments"] = False
    osrm_out.loc[loc1, "isMatchedSegments"] = True

    osrm_out["distance_to_start_node"] = np.nan
    osrm_out.loc[loc1, "distance_to_start_node"] = get_distance(osrm_out.loc[loc1, ["lat", "lon"]].values,
                                                                segments.loc[loc2, ["startLat", "startLon"]].values)

    osrm_out["distance_to_end_node"] = np.nan
    osrm_out.loc[loc1, "distance_to_end_node"] = get_distance(osrm_out.loc[loc1, ["lat", "lon"]].values,
                                                              segments.loc[loc2, ["endLat", "endLon"]].values)

    osrm_out["distance_from_start"] = np.nan
    osrm_out.loc[loc1, "distance_from_start"] = segments.loc[loc2, "distance_from_start"].values + osrm_out.loc[
        loc1, "distance_to_start_node"].values

    out = pd.concat([out, osrm_out], axis=0)
    # print(i)

    if not i % 500:
        print(f"{i} in {data.shape[0]}, percent = {i / data.shape[0] * 100}")

out = out[out["confidence"] >= CONFIDENCE_LEVEL]

time_vector = pd.date_range(start='2019-11-18 08:00:00',
                            end='2019-11-18 10:00:00',
                            freq='30min')
route_addition = np.arange(0, time_vector.shape[0], 1) * 100

for i, time in enumerate(time_vector[:-1]):
    index = (out["raw_time"] >= time) & (out["raw_time"] < time_vector[i+1])
    out.loc[index, "route_id"] = out.loc[index, "route_id"] + route_addition[i]


out =out.reset_index(drop=True)
