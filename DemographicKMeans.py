import pandas as pd
import numpy as np
import glob
import os

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")

files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

print("Dataset shape:", df.shape)
print(df.columns)

exclude_cols = ["date", "state", "district", "pincode"]

demo_cols = [
    c for c in df.select_dtypes(include="number").columns
    if c not in exclude_cols
]

df["total_updates"] = df[demo_cols].sum(axis=1)

state_features = (
    df.groupby("state")
    .agg(
        avg_updates=("total_updates", "mean"),
        std_updates=("total_updates", "std"),
        max_updates=("total_updates", "max")
    )
    .reset_index()
)

state_features = state_features.fillna(0)
print(state_features.head())

X = state_features[["avg_updates", "std_updates", "max_updates"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

inertia = []

for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X_scaled)
    inertia.append(km.inertia_)

plt.figure()
plt.plot(range(2, 8), inertia, marker="o")
plt.xlabel("Number of clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method for K-Means")
plt.show()

kmeans = KMeans(n_clusters=3, random_state=42)
state_features["cluster"] = kmeans.fit_predict(X_scaled)

print(state_features[["state", "cluster"]])

plt.figure()
for c in state_features["cluster"].unique():
    subset = state_features[state_features["cluster"] == c]
    plt.scatter(
        subset["avg_updates"],
        subset["std_updates"],
        label=f"Cluster {c}"
    )

plt.xlabel("Average Updates")
plt.ylabel("Update Variability")
plt.title("K-Means Clustering of Demographic Update Patterns")
plt.legend()
plt.show()
