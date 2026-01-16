# ---------------------------------------------------------
# Time Series Forecasting using ARIMA
# Aadhaar Daily Enrolment Forecast
# ---------------------------------------------------------

import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
enrolment_path = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")

# --------------------------------------------------
# LOAD ENROLMENT FILES (RECURSIVE)
# --------------------------------------------------
enrolment_files = glob.glob(
    os.path.join(enrolment_path, "**", "*.csv"),
    recursive=True
)

if not enrolment_files:
    raise ValueError("No enrolment files found")

df_enrol = pd.concat(
    (pd.read_csv(f) for f in enrolment_files),
    ignore_index=True
)

# --------------------------------------------------
# DATE + FEATURE ENGINEERING
# --------------------------------------------------
df_enrol["date"] = pd.to_datetime(df_enrol["date"], format="%d-%m-%Y")

df_enrol["total_enrolment"] = (
    df_enrol["age_0_5"] +
    df_enrol["age_5_17"] +
    df_enrol["age_18_greater"]
)

daily_enrol = (
    df_enrol.groupby("date")["total_enrolment"]
    .sum()
    .reset_index()
    .sort_values("date")
)

daily_enrol.set_index("date", inplace=True)

# --------------------------------------------------
# TRAIN–TEST SPLIT (80–20)
# --------------------------------------------------
train_size = int(len(daily_enrol) * 0.8)
train = daily_enrol.iloc[:train_size]
test = daily_enrol.iloc[train_size:]

# --------------------------------------------------
# ARIMA MODEL (p,d,q) = (1,1,1)
# --------------------------------------------------
model = ARIMA(train, order=(1, 1, 1))
model_fit = model.fit()

# --------------------------------------------------
# FORECAST
# --------------------------------------------------
forecast_steps = len(test)
forecast = model_fit.forecast(steps=forecast_steps)

# --------------------------------------------------
# PLOT RESULTS
# --------------------------------------------------
plt.figure()
plt.plot(train.index, train, label="Train Data")
plt.plot(test.index, test, label="Actual Data")
plt.plot(test.index, forecast, label="ARIMA Forecast")
plt.title("ARIMA Forecast of Daily Aadhaar Enrolment")
plt.xlabel("Date")
plt.ylabel("Total Enrolment")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("ARIMA forecasting completed successfully.")
