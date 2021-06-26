#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import concurrent.futures
import pickle
import json
import subprocess

import numpy as np
import pandas as pd
from scipy import interpolate

segments = pd.read_csv('segments.csv')

#%%
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
# In[]    
            
# 8-10 verisi
            
#data = pd.read_csv("raw_data/08_00-10_00.csv", header=0, names=["damped","arac_id","tarih","longitude","latitude","time"])
#data = data.drop(columns=["damped"])
#data["time"] = pd.to_datetime(data['tarih'], format="%Y%m%d%H%M%S")
#data['UNIX_TIMESTAMP'] = data['time'].astype(np.int64) // 10**9
#data = data.sort_values(by=["arac_id","time"])
#data.reset_index(inplace=True,drop=True)
#
#data = data.drop_duplicates(['arac_id', 'time', 'latitude','longitude'],keep= 'first')
#data = data.drop_duplicates(['arac_id', 'latitude','longitude'],keep= False)

#%%
#data = pd.read_csv("raw_data/ON_DECEMBER_TABLE_2-9_DECEMBER.csv", header=0, names=["arac_id","tarih","longitude","latitude","aux1","aux2","aux3"])
#data = pd.read_csv("raw_data/ON_DECEMBER_TABLE_2-9_DECEMBER.csv", header=0, usecols=[0, 1, 2, 3])
data = pd.read_csv("raw_data/december_23_30.csv", header=0)
#data = data.drop(columns=["aux1","aux2","aux3"])
data.columns = ["arac_id", "tarih", "longitude", "latitude"]
data["time"] = pd.to_datetime(data['tarih'], format="%Y%m%d%H%M%S")
data['UNIX_TIMESTAMP'] = data['time'].astype(np.int64) // 10**9
data = data.sort_values(by=["arac_id","time"])
data.reset_index(inplace=True,drop=True)

data = data.drop_duplicates(['arac_id', 'time', 'latitude','longitude'],keep= 'first')
data = data.drop_duplicates(['arac_id', 'latitude','longitude'],keep= False)

# %%

def get_matched_data(arac_data):
    arac_id = arac_data["arac_id"].iloc[0]
        
    if len(arac_data["longitude"]) <=2:
#        print(f"not enough gps points arac_id:{arac_id}")
#        return {"message":f"gps point less than 2 arac_id:{arac_id}"}
        raise Exception(f"gps point less than 2 arac_id:{arac_id}")
    
    options = {
        'coordinates': pd.concat([arac_data["longitude"],arac_data["latitude"]],axis=1).to_numpy(),
        'timestamps': arac_data["UNIX_TIMESTAMP"].to_numpy(),
        'radiuses': np.ones(len(arac_data)) * 15
        }
    
    p = subprocess.Popen(['node', 'index.js'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    data = json.dumps(options, cls=NpEncoder)
    response = p.communicate(data.encode())[0]
    
#    try:
    match = json.loads(response)
        
    if match["status"]:
        match["trace_time"] = arac_data["tarih"].to_numpy()
        match["arac_id"] = arac_id
        return match
    else:
        raise Exception(f"map matching returned False arac_id:{arac_id}")
        
#        print(f"not matched arac_id:{arac_id}")
#        return {"message": "map matching returned False"}
#        raise Exception(f"map matching returned False arac_id:{arac_id}")
#    
#    except Exception as e:
##        print(f"error occured arac_id:{arac_id}", e)
#        return {"message": e}
#    
#%%
    
#8 -10 data 
##periods = pd.date_range(start=data["time"].min().date(), end=data["time"].max().date(), freq="D")
#matches = [] # for each day create empty
##subdata = data[(data["time"] >= periods[0]) & (data["time"] < periods[1])]
##arac_id = "135aa8d" #büyük
##arac_id = "05000qx" #küçük
#arac_id = data["arac_id"].unique()
#for arac in arac_id[[3]]:
#    arac_data = data[data["arac_id"] == arac]
#    p = get_matched_data(arac_data)
#    matches.append(p)


#%%
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


def get_osrm_out(match_result, segments):
    arac_id = match_result["arac_id"]
    confidence = np.array(match_result["response"]["confidence"])
    
    
    
    zip_iterator = zip(match_result["response"]["tracepoints"],
                       match_result["response"]["matchings_index"],
                       match_result["trace_time"])
    
    tracepoints ,matchings_index, trace_time= zip(*[(tracepoints ,matchings_index, trace_time) for tracepoints, matchings_index, trace_time in zip_iterator if tracepoints is not None])
    
    n_data = len(tracepoints)
    
    osrm_out = pd.DataFrame(tracepoints, columns=["lon","lat"])
    osrm_out.insert(0, "arac_id", arac_id)
    osrm_out["time"] = trace_time
    osrm_out["route_id"] = matchings_index
    osrm_out["confidence"] = confidence[list(matchings_index)]
    
    nodes = []
    
    for match in match_result["response"]["matchings"]:
        for point in match:
            nodes.append([point[0], point[1]])
        nodes.append([match[-1][-2], match[-1][-1]])
        
    osrm_out["start_node"] , osrm_out["end_node"] = zip(*nodes)
    
    osrm_out[["start_node", "end_node"]].to_numpy()
    segments[["start_node", "end_node"]].to_numpy()
    
    loc1, loc2 = np.equal(osrm_out[["start_node", "end_node"]].to_numpy()[:,None,:], segments[["start_node", "end_node"]].to_numpy()[None,:,:]).all(axis=-1).nonzero()
    
    osrm_out["dir"] = pd.array([np.nan]*n_data, dtype="Int64")
    osrm_out.loc[loc1, "dir"] = segments.loc[loc2, "dir"].to_numpy()
    
    osrm_out["segment_id"] = pd.array([np.nan]*n_data, dtype="Int64")
    osrm_out.loc[loc1, "segment_id"] = segments.loc[loc2, "segment_id"].values
    
    osrm_out["isMatchedSegments"] = False
    osrm_out.loc[loc1, "isMatchedSegments"] = True
    
    
    osrm_out["distance_to_start_node"] = np.nan
    osrm_out.loc[loc1, "distance_to_start_node"] = get_distance(osrm_out.loc[loc1, ["lat", "lon"]].to_numpy(),
                                                                segments.loc[loc2, ["startLat", "startLon"]].to_numpy())
    
    osrm_out["distance_to_end_node"] = np.nan
    osrm_out.loc[loc1, "distance_to_end_node"] = get_distance(osrm_out.loc[loc1, ["lat", "lon"]].to_numpy(),
                                                              segments.loc[loc2, ["endLat", "endLon"]].to_numpy())
    
    
    osrm_out["distance_from_start"] = np.nan
    osrm_out.loc[loc1, "distance_from_start"] = segments.loc[loc2, "distance_from_start"].to_numpy() + osrm_out.loc[loc1, "distance_to_start_node"].to_numpy()
    
    
    
    osrm_out = osrm_out[osrm_out["isMatchedSegments"]]
    
#    return osrm_out.groupby("route_id").filter(delete_useless_data)
    osrm_out = osrm_out.groupby("route_id").filter(delete_useless_data)
    
    if osrm_out.empty:
        raise Exception(f"osrm is empty arac_id: {arac_id}")
    else:
        return osrm_out
        
    
def delete_useless_data(route_data):
    
#    route_id = route_data["route_id"].iloc[0]
        
    route_data = route_data[route_data["isMatchedSegments"]]
    route_data = route_data.drop_duplicates(subset=["time"], ignore_index=True)
    route_data = route_data.drop_duplicates(subset=["distance_from_start"], ignore_index=True)
    
    if len(route_data.index) < 2:
#            print("go go")
#            raise Exception(f"Number of gps points is less than 2: arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
        return False
    
    if len(route_data["dir"].drop_duplicates().index) > 1:
#            print("route contains multiple directions")
#            raise Exception(f"Route contains multiple directions arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
        return False
    
    route_data = route_data.sort_values("time")
    
    first_ii = \
        np.equal(route_data.iloc[0]["segment_id"].astype('int'),
                 segments["segment_id"].to_numpy()).nonzero()[0]
    last_ii = \
        np.equal(route_data.iloc[-1]["segment_id"].astype('int'),
                 segments["segment_id"].to_numpy()).nonzero()[0]

    if (first_ii.shape[0] == 0) | (last_ii.shape[0] == 0):
        # raise NotImplementedError
#            print(f"arac_id= {arac} undefined route ({route_id}) start (or end)")
#            raise Exception(f"start node OR end node cannot be found in list arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
        return False
    
    first_ii = first_ii.item()
    last_ii = last_ii.item()
    
    segment_list = segments.loc[first_ii:last_ii, "segment_id"]
    
    if not len(segment_list.index):
#            print("start segment > last segment")
#            raise Exception(f"start node > end node arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
        return False
        
    
    return True

def smooth_osrm_data(osrm_out):
    return osrm_out

def augmentation(osrm_out, segments):
    
    osrm_result = []
    aug_result =[]
    arac_id = osrm_out["arac_id"].iloc[0]

    for route_id, route_data in osrm_out.groupby("route_id"):
        
        route_data = route_data[route_data["isMatchedSegments"]]
        
        if len(route_data.index) < 2:
#            print("go go")
#            raise Exception(f"Number of gps points is less than 2: arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
            continue
            
        route_data = route_data.drop_duplicates(subset=["time"], ignore_index=True)
        route_data = route_data.drop_duplicates(subset=["distance_from_start"], ignore_index=True)
    
        if len(route_data["dir"].drop_duplicates().index) > 1:
#            print("route contains multiple directions")
#            raise Exception(f"Route contains multiple directions arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
            continue
    
        route_data = route_data.sort_values("time")
        
        first_ii = \
            np.equal(route_data.iloc[0]["segment_id"].astype('int'),
                     segments["segment_id"].to_numpy()).nonzero()[0]
        last_ii = \
            np.equal(route_data.iloc[-1]["segment_id"].astype('int'),
                     segments["segment_id"].to_numpy()).nonzero()[0]
    
        if (first_ii.shape[0] == 0) | (last_ii.shape[0] == 0):
            # raise NotImplementedError
#            print(f"arac_id= {arac} undefined route ({route_id}) start (or end)")
#            raise Exception(f"start node OR end node cannot be found in list arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
            continue
    
        first_ii = first_ii.item()
        last_ii = last_ii.item()
        
        segment_list = segments.loc[first_ii:last_ii, "segment_id"]
        
        if not len(segment_list.index):
#            print("start segment > last segment")
#            raise Exception(f"start node > end node arac_id: {arac_id} route_id: {route_data['route_id'].iloc[0]} approx. time {route_data['time'].iloc[0]}")
            continue
            
        space_axis = segments.loc[first_ii:last_ii, "calc_length"]
        space_axis = space_axis.cumsum() - space_axis
            
        segment_comparison = np.equal(route_data["segment_id"].to_numpy()[:, None], segment_list.to_numpy())
        
        # notes:
        # route_data ["time"] çevirmeye gerek var mı
        # data_axis' i ayrı variable'a ata
        # osrm_out'tan sadece route_data'yı topla?
        
        data_axis = space_axis.iloc[segment_comparison.argmax(axis=1)].to_numpy() + route_data["distance_to_start_node"].to_numpy()
        route_data["time"] = pd.to_datetime(route_data["time"], format="%Y%m%d%H%M%S")
    
        aux_date = (route_data["time"] - pd.to_datetime('1900')).dt.total_seconds() # hiç çevirmeden integer datetime'dan git?
        
        f = interpolate.interp1d(data_axis, aux_date,
                             kind="linear", bounds_error=False,
                             fill_value="extrapolate")
        interpolated_time = pd.to_timedelta(f(space_axis.to_numpy()), unit="seconds") + pd.to_datetime('1900')
    
    
    
        
        aug_data = pd.DataFrame(segment_list.to_numpy(), columns=["segment_id"])
        aug_data["segment_id"] = segment_list.to_numpy()
        aug_data["aug_time"] = interpolated_time
        aug_data["aug_type"] = 0
        aug_data.loc[segment_comparison.any(axis=0), "aug_type"] = 1
        aug_data.loc[~segment_comparison.any(axis=0), "aug_type"] = 2
        aug_data["arac_id"] = arac_id
        aug_data["route_id"] = route_id
        aug_data["lat"] = segments.loc[first_ii:last_ii, "startLat"].to_numpy()
        aug_data["lon"] = segments.loc[first_ii:last_ii, "startLon"].to_numpy()
        aug_data["dir"] = segments.loc[first_ii:last_ii, "dir"].to_numpy()
        aug_data["speed"] = 1e-3 * np.diff(space_axis, append=np.nan) / (
                np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h'))
        
        aug_data["time_diff"] = np.diff(aug_data["aug_time"], append=np.datetime64('NaT')) / np.timedelta64(1, 'h')
        aug_data["space_diff"] = 1e-3 * np.diff(space_axis, append=np.nan)
        aug_data = aug_data.drop(aug_data.index[0]) # delete firs one because is it extrapolate towards backward
        
        aug_result.append(aug_data)
        osrm_result.append(route_data)
    
    return pd.concat(osrm_result), pd.concat(aug_result)
    

#%%
def get_processed_data(arac_id, arac_data, segments):
    try:
        matching = get_matched_data(arac_data)
        
        osrm_data = get_osrm_out(matching, segments)
        
        osrm_data = smooth_osrm_data(osrm_data)
        
        osrm_data, aug_data = augmentation(osrm_data, segments)
        return True, osrm_data, aug_data
    except IndexError as e:
#        raise e
        return False, str(e) +  f" arac_id: {arac_id}", None
    except Exception as e:
#        error_list.append({"messae": e})
        return False, str(e) + f" arac_id: {arac_id}", None
#    return osrm_data, aug_data


#%%
        
##periods = pd.date_range(start=data["time"].min().date(), end=data["time"].max().date(), freq="D")
#matches = [] # for each day create empty
#error_list = []
##subdata = data[(data["time"] >= periods[0]) & (data["time"] < periods[1])]
##arac_id = "135aa8d" #büyük
##arac_id = "05000qx" #küçük
#arac_id = "050l3cs"
#arac_data = data[data["arac_id"] == arac_id]
#
#match = get_matched_data(arac_data)
#osrm_out = get_osrm_out(match)
#osrm_out = filter_on_osrm_out(osrm_out)
#osrm_data , aug_data = augmentation(osrm_out)

#try:
#    match = get_matched_data(arac_data)
#    osrm_out = get_osrm_out(match)
#    osrm_out = filter_on_osrm_out(osrm_out)
#    aug_data = augmentation(osrm_out)
#except Exception as e:
#    error_list.append(e)

    
    
        
#a1
#%%
#    # single processor -- debugging puroses 
##periods = pd.date_range(start=data["time"].min().date(), end=data["time"].max().date(), freq="D")
#    
#data2 = data.iloc[:10000]
#osrm = [] # for each day create empty
#aug = []
#error_list = []
##subdata = data[(data["time"] >= periods[0]) & (data["time"] < periods[1])]
##arac_id = "135aa8d" #büyük
##arac_id = "05000qx" #küçük
#for arac_id, arac_data in data2.groupby("arac_id"):
##arac_data = subdata[subdata["arac_id"] == arac_id]
#    status, osrm_data, aug_data = get_processed_data(arac_id, arac_data, segments)
#    if status:
#        osrm.append(osrm_data)
#        aug.append(aug_data)
#    else:
#        error_list.append(osrm_data)
#
#osrm = pd.concat(osrm)
#aug = pd.concat(aug)



#%%

# parallel processing for toy data
#osrm = [] # for each day create empty
#aug = []
#error_list = []
#with concurrent.futures.ProcessPoolExecutor() as executor:
#    processes = [executor.submit(get_processed_data, arac_id, arac_data, segments) for arac_id, arac_data in data.groupby("arac_id")]
#    
#    for p in concurrent.futures.as_completed(processes):
#        status, osrm_data, aug_data = p.result()
#        if status:
#            osrm.append(osrm_data)
#            aug.append(aug_data)
#        else:
#            error_list.append(osrm_data)
#
#osrm = pd.concat(osrm)
#aug = pd.concat(aug)


#  CUSTOM EXCEPTION YAP

#%%
periods = pd.date_range(start=data["time"].min().date(), end=data["time"].max().date(), freq="D")


    
for period in periods: ############         periods
    
    osrm = [] # for each day create empty
    aug = []
    error_list = []
    
    subdata = data[(data["time"] >= period) & (data["time"] < (period + period.freq))]
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = [executor.submit(get_processed_data, arac_id, arac_data, segments) for arac_id, arac_data in subdata.groupby("arac_id")]
        
        for p in concurrent.futures.as_completed(processes):
            status, osrm_data, aug_data = p.result()
            if status:
                osrm.append(osrm_data)
                aug.append(aug_data)
            else:
                error_list.append(osrm_data)
                
    osrm = pd.concat(osrm)
    aug = pd.concat(aug)
    

    osrm.to_csv(f"output/osrm_{period.date()}.csv")
    aug.to_csv(f"output/aug_{period.date()}.csv")
#    np.savetxt("output/error_list_{period}.csv",error_list)
    with open(f"output/error_list_{period.date()}.csv", "wb") as f:   #Pickling
        pickle.dump(error_list, f)
    
    print(f"""matching start day: {periods[0].date()}
    matching end day: {periods[-1].date()}
    completed: {period.date()}""")

            
#        with open(f'{period.date()}.json', 'w') as outfile:
#            json.dump(matches, outfile, cls=NpEncoder)
#        print(f"""matching start day: {periods[0].date()}
#        matching end day: {periods[-1].date()}
#        completed: {period.date()}""")

#arac_id = "135aa8d" #büyük
#arac_id = "05000qx" #küçük
