import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

# ----------------------------
# Load Data
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")

files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

# Identify demographic columns
exclude_cols = ["date", "state", "district", "pincode"]
demo_cols = [
    c for c in df.select_dtypes(include="number").columns
    if c not in exclude_cols
]

df["total_demo_updates"] = df[demo_cols].sum(axis=1)

# ----------------------------
# Daily Aggregation
# ----------------------------
daily_updates = (
    df.groupby("date")["total_demo_updates"]
    .sum()
    .reset_index()
)

# ----------------------------
# Burst Detection Logic
# ----------------------------
mean = daily_updates["total_demo_updates"].mean()
std = daily_updates["total_demo_updates"].std()

daily_updates["burst_flag"] = (
    daily_updates["total_demo_updates"] > mean + 2 * std
)

# ----------------------------
# Visualization
# ----------------------------
plt.figure()
plt.plot(daily_updates["date"], daily_updates["total_demo_updates"])
plt.scatter(
    daily_updates[daily_updates["burst_flag"]]["date"],
    daily_updates[daily_updates["burst_flag"]]["total_demo_updates"]
)
plt.title("Demographic Update Burst Detection")
plt.xlabel("Date")
plt.ylabel("Total Updates")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("Burst days detected:")
print(daily_updates[daily_updates["burst_flag"]])
