import pandas as pd
import glob
import os

# ----------------------------
# Load Demographic Dataset
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")

files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

print("Dataset loaded:", df.shape)
print(df.columns)

# ----------------------------
# Identify demographic columns
# ----------------------------
exclude_cols = ["date", "state", "district", "pincode"]

demo_cols = [
    c for c in df.select_dtypes(include="number").columns
    if c not in exclude_cols
]

df["total_demo_updates"] = df[demo_cols].sum(axis=1)

print("Demographic measures used:", demo_cols)

# ----------------------------
# State-wise daily aggregation
# ----------------------------
state_daily = (
    df.groupby(["state", "date"])["total_demo_updates"]
    .sum()
    .reset_index()
)

print(state_daily.head())

# ----------------------------
# Automation rules (NO scoring)
# ----------------------------
state_summary = (
    state_daily
    .groupby("state")["total_demo_updates"]
    .agg(["mean", "std"])
    .reset_index()
)

def automation_rule(row):
    # Stable & predictable → automate
    if row["std"] <= row["mean"] * 0.3:
        return "AUTO_PROCESS"

    # Moderate variation → partial automation
    if row["std"] <= row["mean"] * 0.6:
        return "AUTO_PROCESS_WITH_AUDIT"

    # High variation → manual control
    return "MANUAL_REVIEW"

state_summary["automation_decision"] = (
    state_summary.apply(automation_rule, axis=1)
)

print(state_summary.head())

# ----------------------------
# Final automation plan
# ----------------------------
automation_plan = state_summary[[
    "state", "mean", "std", "automation_decision"
]]

print("\nDemographic Automation Plan:")
print(automation_plan)
