import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
#import pmdarima as pm
plt.close('all')

#%%
aug_data = pd.read_csv('python_aug.csv')

aug_data["aug_time"] = pd.to_datetime(aug_data["aug_time"])
aug_data = aug_data.sort_values(["segment_id", "aug_time"])

selected_segment_id = aug_data["segment_id"].value_counts().idxmax() # segment with max data

data = aug_data[aug_data["segment_id"] == selected_segment_id]

data.set_index("aug_time", inplace=True)
data = data.dropna()
#%%

# data.plot(y="speed", marker=".",color="blue")
# plt.show()

# new_index = pd.date_range(start='2019-11-18 08:00:00', end="2019-11-18 10:00:00", freq="5min")

# data2 = data.resample(new_index).mean()

data2 = data["speed"].resample("2T").mean()

test = data2.iloc[-8:]
data2 = data2.drop(index=data2.iloc[-8:].index)

n_data = data["speed"].resample("2T").count()

_, ax = plt.subplots()
data.plot(y="speed", marker=".", color="blue", ax=ax, label="raw", linestyle="none")
data2.plot(marker=".", color="red", ax=ax, label="avg")
test.plot(marker=".", color="yellow", ax=ax, label="test")
plt.show()
#%%
# data2 =
station = adfuller(data2)

print(station)

plot_acf(data2, zero=False)
plot_pacf(data2, zero=False)

model_results = []

# Loop over p values from 0-2
for p in range(3):
    # Loop over q values from 0-2
    for d in range(2):
        for q in range(3):

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
# model_results.rename(columns={"p", "d", "q", "aic", "bic"})
#%%
model_results.sort_values("aic")

model_results.sort_values("bic")

# selected order = (1,0,1) and (0,1,1) (ikinci biraz anlamsız)

model = SARIMAX(data2, order=(0, 1, 1), trend='c')
results = model.fit()

# model2 = SARIMAX(data2, order=(0, 1, 1))
# results2 = model2.fit()

#%%
results.plot_diagnostics()
plt.show()


#%%

fcast = results.get_forecast(10).summary_frame(alpha=0.1)
# fcast.

fig, ax = plt.subplots()

data2.plot(ax=ax)
fcast['mean'].plot(ax=ax, style='k--')
ax.fill_between(fcast.index, fcast['mean_ci_lower'], fcast['mean_ci_upper'], color='k', alpha=0.1)
plt.show()
