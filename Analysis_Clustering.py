
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from aadhaar_core import AadhaarDataManager, setup_visuals

colors = setup_visuals()
manager = AadhaarDataManager()
df_enrol, df_demo, df_bio = manager.get_all_data()

def state_clustering_analysis():
    print("[1/2] Clustering States by Identity Maturity...")
    
    # Merge metrics
    enrol_stats = df_enrol.groupby("state")["total_enrolment"].sum().reset_index()
    demo_stats = df_demo.groupby("state")["total_demo_updates"].sum().reset_index()
    bio_stats = df_bio.groupby("state")["total_bio_updates"].sum().reset_index()
    
    combined = enrol_stats.merge(demo_stats, on="state").merge(bio_stats, on="state")
    
    # Feature for maturity: Ratio of Updates to Enrolments
    combined["saturation_ratio"] = (combined["total_demo_updates"] + combined["total_bio_updates"]) / (combined["total_enrolment"] + 1)
    
    X = combined[["total_enrolment", "saturation_ratio"]]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=3, random_state=42)
    combined["cluster"] = kmeans.fit_predict(X_scaled)
    
    # Rename clusters for business meaning
    cluster_map = {
        combined.groupby("cluster")["saturation_ratio"].mean().idxmin(): "Growth Phase (High Enrolment)",
        combined.groupby("cluster")["saturation_ratio"].mean().sort_values().index[1]: "Stable Ecosystem",
        combined.groupby("cluster")["saturation_ratio"].mean().idxmax(): "Mature (Heavy Maintenance)"
    }
    combined["Maturity Level"] = combined["cluster"].map(cluster_map)
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=combined, x="total_enrolment", y="saturation_ratio", hue="Maturity Level", size="total_bio_updates", sizes=(100, 1000), palette="deep", alpha=0.7)
    
    plt.title("State Identity Lifecycle Clustering: Maturity vs New Enrolment")
    plt.xlabel("Total New Enrolments")
    plt.ylabel("Updates per Enrolment (Saturation Index)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    save_path = "DataVisualisation/State_Maturity_Clusters.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    plt.show()
    plt.close()
    
    return combined

if __name__ == "__main__":
    state_clustering_analysis()
    print("Clustering Analysis Complete.")
