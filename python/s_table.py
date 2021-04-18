import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.close('all')

aug_data = pd.read_csv('python_aug.csv')

segments = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')
segments = segments.set_index("segment_id")

aug_data["aug_time"] = pd.to_datetime(aug_data["aug_time"])
aug_data = aug_data.sort_values(["segment_id", "aug_time"])

aug_data["speed_label"] = np.nan

aug_data.loc[aug_data["speed"] >= 105, "speed_label"] = 0
aug_data.loc[(aug_data["speed"] >= 90) & (aug_data["speed"] < 105), "speed_label"] = 1
aug_data.loc[(aug_data["speed"] >= 75) & (aug_data["speed"] < 90), "speed_label"] = 2
aug_data.loc[(aug_data["speed"] >= 60) & (aug_data["speed"] < 75), "speed_label"] = 3
aug_data.loc[(aug_data["speed"] >= 45) & (aug_data["speed"] < 60), "speed_label"] = 4
aug_data.loc[(aug_data["speed"] >= 30) & (aug_data["speed"] < 45), "speed_label"] = 5
aug_data.loc[(aug_data["speed"] >= 15) & (aug_data["speed"] < 30), "speed_label"] = 6
aug_data.loc[aug_data["speed"] < 15, "speed_label"] = 7

aug_data["label_change"] = aug_data["speed_label"].diff()
aug_data["pos_label_change"] = aug_data.loc[aug_data["label_change"] > 0, ["label_change"]]
aug_data["neg_label_change"] = aug_data.loc[aug_data["label_change"] < 0, ["label_change"]]
# aug_data["label_change"] = ~(aug_data["speed_label"].diff().isin([0.0, np.nan]))


s_table = pd.DataFrame(index=aug_data["segment_id"].unique())

s_table["length"] = segments["calc_length"]
s_table["distance_from_start"] = segments["distance_from_start"]
s_table["dir"] = segments["dir"]
s_table["n_vehicle"] = aug_data.groupby("segment_id").apply(lambda x: x["arac_id"].unique().size)
s_table["n_route"] = aug_data.groupby("segment_id")["route_id"].count()  # route count = row sayısı
s_table["tt_mean"] = aug_data.groupby("segment_id")["time_diff"].mean()
s_table["tt_mean_speed"] = 1e-3 * segments["calc_length"] / s_table["tt_mean"]
s_table["std"] = aug_data.groupby("segment_id")["speed"].std()
s_table["n_pos_label_ratio"] = aug_data.groupby("segment_id")["pos_label_change"].sum() / s_table["n_route"]
s_table["n_neg_label_ratio"] = aug_data.groupby("segment_id")["neg_label_change"].sum() / s_table["n_route"]

start_date = pd.to_datetime("2019-11-18 08:00")
end_date = pd.to_datetime("2019-11-18 10:00")
n_time = int((end_date - start_date) / pd.to_timedelta(15, unit="m"))
time_mask = np.zeros((aug_data.shape[0], n_time), dtype=bool)

for i in range(n_time):
    # print(i)
    time_mask[:, i] = (aug_data["aug_time"] >= start_date + i * pd.to_timedelta(15, unit="m")) & \
                      (aug_data["aug_time"] < (start_date + (i + 1) * pd.to_timedelta(15, unit="m")))

# arrays = [["time" + str(i + 1) for i in range(n_time)],
#           ['n_vehicle', 'n_route', 'tt_mean', 'tt_mean_speed', 'std']]

# s_table2 = pd.DataFrame()
# s_table2.columns = pd.MultiIndex.from_product(arrays)


# fig, ax = plt.subplots()
#
# p1 = ax.bar(s_table[s_table["dir"] == 1].index, s_table[s_table["dir"] == 1]["n_vehicle"], width=0.6)
#
# plt.show()

attr_names = ["n_vehicle", "n_route", "tt_mean", "tt_mean_speed", "std", "n_pos_label_ratio", "n_neg_label_ratio"]

for i in range(n_time):
    for name in attr_names:
        s_table["time" + str(i + 1) + name] = np.nan

    s_table["time" + str(i + 1) + attr_names[0]] = aug_data[time_mask[:, i]].groupby("segment_id").apply(
        lambda x: x["arac_id"].unique().size)
    s_table["time" + str(i + 1) + attr_names[1]] = aug_data[time_mask[:, i]].groupby("segment_id")["route_id"].count()
    s_table["time" + str(i + 1) + attr_names[2]] = aug_data[time_mask[:, i]].groupby("segment_id")["time_diff"].mean()
    s_table["time" + str(i + 1) + attr_names[3]] = 1e-3 * segments["calc_length"] / s_table[
        "time" + str(i + 1) + "tt_mean"]
    s_table["time" + str(i + 1) + attr_names[4]] = aug_data[time_mask[:, i]].groupby("segment_id")["speed"].std()
    s_table["time" + str(i + 1) + attr_names[5]] = aug_data[time_mask[:, i]].groupby("segment_id")[
                                                       "pos_label_change"].sum() / s_table[
                                                       "time" + str(i + 1) + "n_route"]
    s_table["time" + str(i + 1) + attr_names[6]] = aug_data[time_mask[:, i]].groupby("segment_id")[
                                                       "neg_label_change"].sum() / s_table[
                                                       "time" + str(i + 1) + "n_route"]


# fig, ax = plt.subplots()
#
# p1 = ax.bar(aug_data[time_mask[:, 0]]["segment_id"].unique(), aug_data[time_mask[:, 0]].groupby("segment_id").apply(lambda x: x["arac_id"].size))
# p2 = ax.bar(aug_data[time_mask[:, 1]]["segment_id"].unique(), aug_data[time_mask[:, 1]].groupby("segment_id").apply(lambda x: x["arac_id"].size),bottom=p1)
# plt.show()


# def get_data_intervarls(x, start_date, end_date, increment_min, time_mask):
#     # n_time = int((end_date - start_date) / pd.to_timedelta(15, unit="m"))
#     n_time = time_mask.shape[1]
#     columns = ["time" + str(i + 1) for i in range(n_time)]
#     d = pd.DataFrame(columns=columns)
#     for i in range(n_time):
#         # print(i)
#         # time_mask = (x["aug_time"] >= start_date + i * increment_min) & \
#         #              (x["aug_time"] < (start_date + (i + 1) * increment_min))
#         d[columns[i]] = x[time_mask].

# aq = aug_data[time_mask[:,0]].groupby("segment_id").agg({'speed':['mean','max']})

# %%

def plot_attr_stacked_bar(s_table, name, n_time, dir):
    fig, ax = plt.subplots()
    aux = s_table[s_table["dir"] == dir]["time1" + name]
    ax.bar(s_table[s_table["dir"] == dir].index, aux, label="delta_t")
    for i in range(n_time - 1):
        # print(i)
        ax.bar(s_table[s_table["dir"] == dir].index, s_table[s_table["dir"] == dir]["time" + str(i + 2) + name],
               bottom=aux, label="delta_t" + str(i + 2))
        aux = aux + s_table[s_table["dir"] == dir]["time" + str(i + 2) + name]
    ax.legend()
    plt.title(name + " dir = " + str(dir))
    plt.show()


plot_attr_stacked_bar(s_table, attr_names[0], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[1], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[2], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[3], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[4], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[5], n_time, 1)
plot_attr_stacked_bar(s_table, attr_names[6], n_time, 1)


# %%

def plot_attr_subplot(s_table, name, n_time, dir):
    fig, axs = plt.subplots(n_time - 1, sharex=True)
    for i, ax in enumerate(axs):
        ax.scatter(s_table[s_table["dir"] == dir].index, s_table[s_table["dir"] == dir]["time" + str(i + 1) + name],
                   label="delta_t" + str(i + 1), s=3)
        ax.set_ylim([0, 50])
    fig.suptitle(name + " dir = " + str(dir))
    plt.show()


plot_attr_subplot(s_table, attr_names[0], n_time, 1)
plot_attr_subplot(s_table, attr_names[1], n_time, 1)
plot_attr_subplot(s_table, attr_names[2], n_time, 1)
plot_attr_subplot(s_table, attr_names[3], n_time, 1)
plot_attr_subplot(s_table, attr_names[4], n_time, 1)
plot_attr_subplot(s_table, attr_names[5], n_time, 1)
plot_attr_subplot(s_table, attr_names[6], n_time, 1)

# %%

fig, axs = plt.subplots(n_time - 1, sharex=True)
for i, ax in enumerate(axs):
    ax.scatter(s_table[s_table["dir"] == 1].index, s_table.loc[s_table["dir"] == 1, ["time" + str(i + 1) + "n_pos_label_ratio"]],
               label="delta_t" + str(i + 1), s=3)
    ax.scatter(s_table[s_table["dir"] == 1].index, s_table.loc[s_table["dir"] == 1, ["time" + str(i + 1) + "n_neg_label_ratio"]],
               label="delta_t" + str(i + 1), s=3)
    ax.set_ylim(None)
# fig.suptitle(name + " dir = " + str(dir))
plt.show()

# %%

# def get_column_names(attr_name): return ["time" + str(i + 1) + attr_name for i in range(n_time)]
#
#
# get_column_names("n_vehicle")
#
# (s_table["n_vehicle"] == s_table[get_column_names("n_vehicle")].sum(axis=1)).all()

#
fig, ax = plt.subplots()
ax.plot(segments.loc[s_table.loc[s_table["dir"] == 1].index, "distance_from_start"],
        s_table.loc[s_table["dir"] == 1, attr_names[5]],
        linewidth=0, marker="o", markersize=2)
plt.show()
# s_table[s_table["dir"] == 1].plot(
#     x=, y=,
# #
# plt.show()
