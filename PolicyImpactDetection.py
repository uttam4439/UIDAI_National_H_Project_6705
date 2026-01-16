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

exclude_cols = ["date", "state", "district", "pincode"]
demo_cols = [
    c for c in df.select_dtypes(include="number").columns
    if c not in exclude_cols
]

df["total_demo_updates"] = df[demo_cols].sum(axis=1)

daily = (
    df.groupby("date")["total_demo_updates"]
    .sum()
    .reset_index()
)

# ----------------------------
# Define Policy Period
# ----------------------------
policy_date = pd.to_datetime("2025-07-01")

before = daily[daily["date"] < policy_date]
after = daily[daily["date"] >= policy_date]

# ----------------------------
# Impact Metrics
# ----------------------------
before_avg = before["total_demo_updates"].mean()
after_avg = after["total_demo_updates"].mean()

increase_percent = ((after_avg - before_avg) / before_avg) * 100

print(f"Average updates BEFORE policy: {before_avg:.2f}")
print(f"Average updates AFTER policy: {after_avg:.2f}")
print(f"Increase due to policy: {increase_percent:.2f}%")

# ----------------------------
# Visualization
# ----------------------------
plt.figure()
plt.plot(daily["date"], daily["total_demo_updates"])
plt.axvline(policy_date)
plt.title("Policy Impact on Demographic Updates")
plt.xlabel("Date")
plt.ylabel("Total Updates")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
