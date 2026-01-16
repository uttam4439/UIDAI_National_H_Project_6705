import pandas as pd
import numpy as np
import glob
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")

files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

exclude_cols = ["date", "state", "district", "pincode"]
demo_cols = [c for c in df.select_dtypes(include="number").columns if c not in exclude_cols]

df["total_demo_updates"] = df[demo_cols].sum(axis=1)

print("Demographic columns:", demo_cols)

state_daily = (
    df.groupby(["state", "date"])["total_demo_updates"]
    .sum()
    .reset_index()
)

state_stats = (
    state_daily
    .groupby("state")["total_demo_updates"]
    .agg(
        mean_updates="mean",
        std_updates="std",
        max_updates="max",
        min_updates="min"
    )
    .reset_index()
)

# Handle division safety
state_stats["std_updates"] = state_stats["std_updates"].fillna(0)

# Coefficient of Variation (stability indicator)
state_stats["cv"] = (
    state_stats["std_updates"] /
    (state_stats["mean_updates"] + 1)
)

def anomaly_ratio(group):
    mean = group.mean()
    std = group.std()
    if std == 0 or np.isnan(std):
        return 0
    anomalies = group[(group > mean + 3*std) | (group < mean - 3*std)]
    return len(anomalies) / len(group)

anomaly_df = (
    state_daily
    .groupby("state")["total_demo_updates"]
    .apply(anomaly_ratio)
    .reset_index(name="anomaly_ratio")
)
state_model = state_stats.merge(anomaly_df, on="state")

# Normalize metrics
state_model["cv_norm"] = state_model["cv"] / state_model["cv"].max()
state_model["anomaly_norm"] = state_model["anomaly_ratio"] / (
    state_model["anomaly_ratio"].max() + 1e-6
)

# Correctness Score (0 to 1)
state_model["correctness_score"] = 1 - (
    0.6 * state_model["cv_norm"] +
    0.4 * state_model["anomaly_norm"]
)

state_model["correctness_score"] = state_model["correctness_score"].clip(0, 1)

print(state_model[["state", "correctness_score"]].head())

def automation_level(score):
    if score >= 0.8:
        return "FULL_AUTO_UPDATE"
    elif score >= 0.6:
        return "PARTIAL_AUTO_UPDATE"
    else:
        return "MANUAL_REVIEW_PRIORITY"

state_model["automation_recommendation"] = (
    state_model["correctness_score"].apply(automation_level)
)

print(state_model[["state", "correctness_score", "automation_recommendation"]])
