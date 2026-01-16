# ---------------------------------------------------------
# Exploratory Data Analysis (EDA) with Measure Aggregation
# Aadhaar Enrolment + Demographic + Biometric
# ---------------------------------------------------------

import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

enrolment_path = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")
demographic_path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")
biometric_path = os.path.join(BASE_DIR, "api_data_aadhar_biometric")

# --------------------------------------------------
# LOAD FILES (RECURSIVE)
# --------------------------------------------------
def load_files(path):
    return glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)

enrolment_files = load_files(enrolment_path)
demographic_files = load_files(demographic_path)
biometric_files = load_files(biometric_path)

print("Enrolment files:", len(enrolment_files))
print("Demographic files:", len(demographic_files))
print("Biometric files:", len(biometric_files))

if not enrolment_files or not demographic_files or not biometric_files:
    raise ValueError("One or more data folders are empty")

# --------------------------------------------------
# CONCATENATE DATA
# --------------------------------------------------
df_enrol = pd.concat((pd.read_csv(f) for f in enrolment_files), ignore_index=True)
df_demo  = pd.concat((pd.read_csv(f) for f in demographic_files), ignore_index=True)
df_bio   = pd.concat((pd.read_csv(f) for f in biometric_files), ignore_index=True)

# --------------------------------------------------
# STANDARDIZE DATE
# --------------------------------------------------
for df in [df_enrol, df_demo, df_bio]:
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

# --------------------------------------------------
# IDENTIFY STATE COLUMN SAFELY
# --------------------------------------------------
def get_state_column(df):
    for col in df.columns:
        if col.lower() == "state":
            return col
    raise ValueError("State column not found")

state_col_enrol = get_state_column(df_enrol)
state_col_demo = get_state_column(df_demo)
state_col_bio = get_state_column(df_bio)

# --------------------------------------------------
# ENROLMENT ANALYSIS
# --------------------------------------------------
df_enrol["total_enrolment"] = (
    df_enrol["age_0_5"] +
    df_enrol["age_5_17"] +
    df_enrol["age_18_greater"]
)

daily_enrol = (
    df_enrol.groupby("date")["total_enrolment"]
    .sum()
    .reset_index()
)

# --------------------------------------------------
# BIOMETRIC ANALYSIS
# --------------------------------------------------
exclude_cols = ["date", state_col_bio, "district"]
bio_cols = [c for c in df_bio.select_dtypes(include="number").columns if c not in exclude_cols]

df_bio["total_biometric_updates"] = df_bio[bio_cols].sum(axis=1)

biometric_trends = (
    df_bio.groupby("date")["total_biometric_updates"]
    .sum()
    .reset_index()
)

# --------------------------------------------------
# DEMOGRAPHIC ANALYSIS (SCHEMA-AGNOSTIC)
# --------------------------------------------------
exclude_cols = ["date", state_col_demo, "district"]
demo_cols = [c for c in df_demo.select_dtypes(include="number").columns if c not in exclude_cols]

df_demo["total_population"] = df_demo[demo_cols].sum(axis=1)

# --------------------------------------------------
# TIME-SERIES VISUALIZATION
# --------------------------------------------------
plt.figure()
plt.plot(daily_enrol["date"], daily_enrol["total_enrolment"])
plt.title("Daily Aadhaar Enrolment Volume")
plt.xlabel("Date")
plt.ylabel("Total Enrolment")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(biometric_trends["date"], biometric_trends["total_biometric_updates"])
plt.title("Daily Aadhaar Biometric Updates")
plt.xlabel("Date")
plt.ylabel("Biometric Updates")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --------------------------------------------------
# ANOMALY VISUALIZATION (Z-score)
# --------------------------------------------------
mean = daily_enrol["total_enrolment"].mean()
std = daily_enrol["total_enrolment"].std()

anomalies = daily_enrol[
    abs(daily_enrol["total_enrolment"] - mean) > 3 * std
]

plt.figure()
plt.plot(daily_enrol["date"], daily_enrol["total_enrolment"])
plt.scatter(anomalies["date"], anomalies["total_enrolment"])
plt.title("Daily Enrolment with Anomalies Highlighted")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --------------------------------------------------
# STATE-WISE AGGREGATION
# --------------------------------------------------
state_enrolment = (
    df_enrol.groupby(state_col_enrol)["total_enrolment"]
    .sum()
    .reset_index()
    .sort_values("total_enrolment", ascending=False)
)

state_population = (
    df_demo.groupby(state_col_demo)["total_population"]
    .sum()
    .reset_index()
)

state_biometric = (
    df_bio.groupby(state_col_bio)["total_biometric_updates"]
    .sum()
    .reset_index()
)

state_combined = (
    state_enrolment
    .merge(state_population, on=state_col_enrol)
    .merge(state_biometric, on=state_col_enrol)
)

print("\nState-wise combined data:")
print(state_combined.head())

# --------------------------------------------------
# STATE-WISE VISUALIZATION
# --------------------------------------------------
top_states = state_enrolment.head(10)

plt.figure()
plt.bar(top_states[state_col_enrol], top_states["total_enrolment"])
plt.title("Top 10 States by Aadhaar Enrolment")
plt.xlabel("State")
plt.ylabel("Total Enrolment")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("\nPipeline executed successfully.")

# ----------------------------------------------
# Demographic vs Biometric Update Comparison
# ----------------------------------------------

total_demographic_updates = df_demo["total_population"].sum()
total_biometric_updates = df_bio["total_biometric_updates"].sum()

print("Total Demographic Updates:", total_demographic_updates)
print("Total Biometric Updates:", total_biometric_updates)

update_types = ["Demographic Updates", "Biometric Updates"]
update_counts = [total_demographic_updates, total_biometric_updates]

plt.figure()
plt.bar(update_types, update_counts)
plt.xlabel("Update Type")
plt.ylabel("Number of Requests")
plt.title("Demographic vs Biometric Aadhaar Update Requests")
plt.tight_layout()
plt.show()
