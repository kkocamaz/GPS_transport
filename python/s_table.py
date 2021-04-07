import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

aug_data = pd.read_csv('python_aug.csv')

segments = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')
segments = segments.set_index("segment_id")

aug_data["aug_time"] = pd.to_datetime(aug_data["aug_time"])
aug_data = aug_data.sort_values(["segment_id", "aug_time"])

aq = aug_data.groupby(["segment_id"]).apply(lambda x: (x["aug_time"].shift(-1) - x["aug_time"]).mean())


s_table = pd.DataFrame(index=aug_data["segment_id"].unique())

s_table["length"] = segments["calc_length"]
s_table["distance_from_start"] = segments["distance_from_start"]
s_table["dir"] = segments["dir"]

s_table["n_vehicle"] = aug_data.groupby("segment_id").apply(lambda x: x["arac_id"].size)

s_table["n_route"] = aug_data.groupby("segment_id")["route_id"].count() # route count = row sayısı

s_table["tt_mean"] = aug_data.groupby("segment_id")["time_diff"].mean()

s_table["tt_mean_speed"] = s_table["tt_mean"] / segments["calc_length"]

s_table["std"] = aug_data.groupby("segment_id")["speed"].std()

start_date = pd.to_datetime("2019-11-18 08:00")
end_date = pd.to_datetime("2019-11-18 10:00")
n_time = int((end_date - start_date) / pd.to_timedelta(15, unit="m"))
time_mask = np.zeros((aug_data.shape[0], n_time), dtype=bool)

for i in range(n_time):
    print(i)
    time_mask[:, i] = (aug_data["aug_time"] >= start_date + i * pd.to_timedelta(15, unit="m")) & \
                      (aug_data["aug_time"] < (start_date + (i+1) * pd.to_timedelta(15, unit="m")))


fig, ax = plt.subplots()

p1 = ax.bar(s_table[s_table["dir"] == 1].index, s_table[s_table["dir"] == 1]["n_vehicle"], width= 0.6)

plt.show()

fig, ax = plt.subplots()

p1 = ax.bar(s_table.index, aug_data[time_mask[:,0]].groupby("segment_id").apply(lambda x: x["arac_id"].size))

plt.show()