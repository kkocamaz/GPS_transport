import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
# %%

path_str = "C:/Users/k/Desktop/output/"
filenames = [path_str + f"aug_2019-12-0{i}.csv" for i in range(2, 9)]

data = pd.concat((pd.read_csv(f) for f in filenames))
segments = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/segments.csv')
markers = pd.read_csv('C:/Users/k/Desktop/GitHub/GPS_transport/input_data/python/markers.csv')

# %%
data["aug_time"] = pd.to_datetime(data["aug_time"], format="%Y-%m-%d %H:%M:%S.%f")
data["date"] = data["aug_time"].dt.date

# %%
data.set_index([data.columns.values[0]], inplace=True)
data.index.name = None

segments.set_index(["segment_id"], inplace=True, verify_integrity=True)

# %%

data[["segment_id", "speed"]].groupby(["segment_id"]).mean(["speed"]).plot(kind="line", use_index=True, y="speed")
plt.title("haftalık ortalama")
plt.show()

# %%
selected_dir = 1
fig, axes = plt.subplots(7, 1, sharex=True, sharey=True)
data.loc[data["dir"] == selected_dir, ["segment_id", "speed", "date"]].groupby(["segment_id", "date"]).mean(["speed"]).unstack()\
    .plot(kind="line", use_index=True, y="speed", subplots=True, ax=axes)
fig.suptitle(f"günlük ortalama speed vs segment id dir {selected_dir}")
plt.show()


selected_dir = 2
fig, axes = plt.subplots(7, 1, sharex=True, sharey=True)
data.loc[data["dir"] == selected_dir, ["segment_id", "speed", "date"]].groupby(["segment_id", "date"]).mean(["speed"]).unstack()\
    .plot(kind="line", use_index=True, y="speed", subplots=True, ax=axes)
fig.suptitle(f"günlük ortalama speed vs segment id dir {selected_dir}")
plt.show()


# %%

# selected_dir = 1
# fig, axes = plt.subplots(nrows=7, ncols=1)
# # axes[0].set_ylim([-10, 200])
# flierprops = dict(marker='.', markerfacecolor='red', markersize=5, markeredgecolor='none')
# data.loc[data["dir"] == selected_dir, ["segment_id", "speed", "date"]].groupby(["date"])\
#     .boxplot(column="speed", by="segment_id", grid=False, flierprops=flierprops, subplots=True, rot=90, ax=axes, sharex=True)
# [ax.set_ylim(-10, 200) for ax in axes]
# fig.suptitle(f"günlük speed distr over segment id dir {selected_dir}")
# plt.show()

# %%

selected_segment_id = 30
_, ax = plt.subplots()
ax.plot(data.loc[data["segment_id"] == selected_segment_id, "aug_time"],
        data.loc[data["segment_id"] == selected_segment_id, "speed"], marker=".", linestyle="none")
plt.xticks(rotation=45)
plt.title("selected segment speed vs time")
plt.show()

plt.rcParams
# %%
fig, ax = plt.subplots(3, 1)
data.loc[data["segment_id"] == selected_segment_id, ["speed", "aug_time"]].sort_values("aug_time"). \
    set_index("aug_time").rolling(window="1T").mean().plot(marker=".", linestyle="none", markersize=4, ax=ax[0])
data.loc[data["segment_id"] == selected_segment_id, ["speed", "aug_time"]].sort_values("aug_time"). \
    set_index("aug_time").rolling(window="2T").mean().plot(marker=".", linestyle="none", markersize=4, ax=ax[1])
data.loc[data["segment_id"] == selected_segment_id, ["speed", "aug_time"]].sort_values("aug_time"). \
    set_index("aug_time").rolling(window="5T").mean().plot(marker=".", linestyle="none", markersize=4, ax=ax[2])
ax[0].get_xaxis().set_visible(False)
ax[0].set_title("1 min window")
ax[1].get_xaxis().set_visible(False)
ax[1].set_title("2 min window")
ax[2].set_title("5 min window")
fig.suptitle("speed of a selected segment with MA in time")
fig.show()

# %%
# fig, ax = plt.subplots(nrows=2, ncols=1, sharey=True)
fig, ax = plt.subplots()
ax.plot([100, 100], [0, 6000])
data["segment_id"].value_counts().sort_index().plot(kind="bar")
# data[data["dir"] == 1].groupby("segment_id").size().plot(kind="bar", ax=ax)
# data[data["dir"] == 2].groupby("segment_id").size().plot(kind="bar", ax=ax[1])
# # ax[0].get_xaxis().set_visible(False)
# ax[0].set_title("dir=1")
# # ax[1].get_xaxis().set_visible(False)
# ax[1].set_title("dir=2")

# ax[0].plot(np.tile(markers["segment_id"].to_numpy(), (2, 1)), ax[0].get_ylim(), alpha=0.5, linewidth=1)

# ax9 = ax.twinx()
#
# ax9.plot(np.tile(markers["segment_id"].to_numpy(), (2, 1)), ax[1].get_ylim(), alpha=0.5, linewidth=1)

# fig.suptitle("gps count vs segments")
plt.show()

# def deco(func):
#     def wrapper(a, *args, **kwargs):
#         # args = [2 * arg for arg in args]
#         print(a, args)
#         return func(a, *args, **kwargs)
#
#     return wrapper
#
# @deco
# def amk(x, y=1):
#     return x ** 2 + y
#
#
# # print("giriş")
# amk(4,5)

# %%

fig, ax = plt.subplots()

ax.bar(data[data["dir"] == 1].groupby("segment_id").size().index.to_numpy(),
       data[data["dir"] == 1].groupby("segment_id").size().to_numpy())

ax.plot([100, 100], [0, 6000])
plt.show()

# %%

df = pd.DataFrame({"segments": [2, 2, 2, 5, 3, 3, 3, 4, 4], "values": [1, 2, 3, 4, 5, 6, 7, 8, 9]})
df.groupby("segments").size().plot(kind="bar")

plt.plot([3, 3], [0, 5])

# %%
df = pd.DataFrame({"segments": [2, 2, 2, 5, 3, 3, 3, 4, 4], "values": [1, 2, 3, 4, 5, 6, 7, 8, 9]})
df.groupby("segments").size().plot(kind="bar", use_index=False)

plt.plot([3, 3], [0, 5])

# %%
aq = data[data["dir"] == 1]
fig, ax = plt.subplots()

ax.bar(np.sort(aq["segment_id"].unique()),
       aq["segment_id"].value_counts().sort_index().to_numpy()
       )
ax.plot(np.tile(markers[markers["dir"] == 1]["segment_id"].to_numpy(), (2, 1)), ax.get_ylim(), alpha=0.5, linewidth=1)
plt.show()

#%%

aq = data[data["dir"] == 1].value_counts("segment_id").reset_index()

#%%
data[data["dir"] == 1].groupby("segment_id").size().reset_index(name="y").plot(kind="bar", x="segment_id", y="y")
# plt.plot([100, 100], [0, 6000])
# plt.show()


#%%

data2 = data.loc[data["segment_id"] == selected_segment_id,["aug_time","speed"]].sort_values("aug_time").set_index("aug_time").rolling(window="5T").mean()

data2 = data2[data2 < 140]


# data2 = data2["speed"].resample("5T").mean()
data2.plot(marker=".", color="red", label="avg")
plt.show()

#%%

data2 = data2.resample("5T").mean()
data2 = data2.dropna()

test = data2.iloc[-150:]
data2 = data2.drop(index=data2.iloc[-150:].index)

_, ax = plt.subplots()
data2.plot(marker=".", color="red", label="avg", ax=ax)
test.plot(marker=".", color="blue",  label="test", ax=ax)
plt.show()

# %%

station = adfuller(data2)

print(station)

# %%

plot_acf(data2, zero=False)
plt.show()

#%%
plot_acf(data2, zero=False, lags=np.arange(30)+210)
plt.show()

#%%
plot_pacf(data2, zero=False)
plt.show()

# %%


model_results = []

# Loop over p values from 0-2
for p in range(10):
    # Loop over q values from 0-2
    for d in range(2):
        for q in range(10):

            try:
                # create and fit ARMA(p,q) model
                model = SARIMAX(data2, order=(p, d, q))
                results = model.fit()

                # Print order and results
                # print(p, q, results.aic, results.bic)
                model_results.append((p, d, q, results.aic, results.bic))
            except:
                # print
                model_results.append((p, d, q, None, None))

model_results = pd.DataFrame(data=model_results, columns=["p", "d", "q", "aic", "bic"])

#%%

model_results.sort_values("aic")

model_results.sort_values("bic")

#%%

model = SARIMAX(data2, order=(2, 1, 9))
results = model.fit()

#%%

results.plot_diagnostics()
plt.show()

#%%

fcast = results.get_forecast(150).summary_frame(alpha=0.1)
# fcast.

fig, ax = plt.subplots()

data2["speed"].plot(ax=ax)
fcast['mean'].plot(ax=ax, style='k--')
plt.show()
#%%

ax.fill_between(fcast.index, fcast['mean_ci_lower'], fcast['mean_ci_upper'], color='k', alpha=0.1)
plt.show()