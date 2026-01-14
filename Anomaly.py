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
# LOAD FILES (RECURSIVE — IMPORTANT FIX)
# --------------------------------------------------
enrolment_files = glob.glob(
    os.path.join(enrolment_path, "**", "*.csv"),
    recursive=True
)

demographic_files = glob.glob(
    os.path.join(demographic_path, "**", "*.csv"),
    recursive=True
)

biometric_files = glob.glob(
    os.path.join(biometric_path, "**", "*.csv"),
    recursive=True
)

print("Enrolment files:", len(enrolment_files))
print("Demographic files:", len(demographic_files))
print("Biometric files:", len(biometric_files))

print("Sample enrolment file:", enrolment_files[:1])

if not enrolment_files or not demographic_files or not biometric_files:
    raise ValueError("One or more folders contain no CSV files")

# --------------------------------------------------
# CONCATENATE DATA
# --------------------------------------------------
df_enrol = pd.concat((pd.read_csv(f) for f in enrolment_files), ignore_index=True)
df_demo  = pd.concat((pd.read_csv(f) for f in demographic_files), ignore_index=True)
df_bio   = pd.concat((pd.read_csv(f) for f in biometric_files), ignore_index=True)

# --------------------------------------------------
# DATE STANDARDIZATION
# --------------------------------------------------
for df in [df_enrol, df_demo, df_bio]:
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

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
# DEMOGRAPHIC ANALYSIS (FULLY SCHEMA-AGNOSTIC)
# --------------------------------------------------

exclude_cols = ["date", "state", "district"]

numeric_cols = df_demo.select_dtypes(include="number").columns.tolist()
numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

print("Demographic numeric columns:", numeric_cols)

if not numeric_cols:
    raise ValueError("No numeric demographic columns found")

df_demo["total_population"] = df_demo[numeric_cols].sum(axis=1)

district_demo = (
    df_demo.groupby("district")["total_population"]
    .sum()
    .reset_index()
)


# --------------------------------------------------
# BIOMETRIC ANALYSIS (SCHEMA-SAFE)
# --------------------------------------------------
exclude_cols = ["date", "state", "district"]
bio_cols = [c for c in df_bio.columns if c not in exclude_cols]

df_bio["total_biometric_updates"] = df_bio[bio_cols].sum(axis=1)

biometric_trends = (
    df_bio.groupby("date")["total_biometric_updates"]
    .sum()
    .reset_index()
)

# --------------------------------------------------
# CROSS-DATASET MERGES
# --------------------------------------------------
combined_time = pd.merge(
    daily_enrol,
    biometric_trends,
    on="date",
    how="inner"
)

enrol_by_district = (
    df_enrol.groupby("district")["total_enrolment"]
    .sum()
    .reset_index()
)

district_merge = enrol_by_district.merge(
    district_demo,
    on="district",
    how="inner"
)

# --------------------------------------------------
# FINAL CHECK
# --------------------------------------------------
print("Demographic columns:", df_demo.columns)
print("Pipeline executed successfully.")

plt.plot(daily_enrol["date"], daily_enrol["total_enrolment"])
plt.plot(biometric_trends["date"], biometric_trends["total_biometric_updates"])

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

