
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from aadhaar_core import AadhaarDataManager, setup_visuals

colors = setup_visuals()
manager = AadhaarDataManager()
df_enrol, df_demo, df_bio = manager.get_all_data()

def analyze_center_pressure():
    print("[1/1] Analyzing Center Pressure & Risk Scores...")
    
    # Calculate current usage vs capacity (simulated capacity)
    # Let's assume most states have a capacity proportional to their population density or historical max
    state_metrics = df_enrol.groupby("state").agg({
        "total_enrolment": "sum",
        "age_0_5": "sum",
        "age_5_17": "sum"
    }).reset_index()
    
    # Simulate Capacity (based on historical peak + 20% buffer)
    state_metrics["capacity"] = state_metrics["total_enrolment"] * 1.2
    
    # Calculate "Pressure Score"
    # High student population + high current enrolment = High Pressure
    state_metrics["pressure_score"] = (state_metrics["total_enrolment"] / state_metrics["capacity"]) * 100
    
    # Risk logic: If student activity is > 40% of total, it's a "Seasonal Risk"
    state_metrics["student_ratio"] = state_metrics["age_5_17"] / state_metrics["total_enrolment"]
    state_metrics["Risk Level"] = np.where(state_metrics["student_ratio"] > 0.4, "High (Seasonal)", "Stable")
    
    top_pressure = state_metrics.sort_values("pressure_score", ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_pressure, x="state", y="pressure_score", hue="Risk Level", palette="magma")
    plt.axhline(90, color='red', linestyle='--', label='Critical Threshold (90%)')
    plt.title("Center Pressure Score: Predicted Resource Utilization by State")
    plt.ylabel("Pressure Score (%)")
    plt.xticks(rotation=45)
    plt.legend()
    
    save_path = "DataVisualisation/Center_Pressure_Risk.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    plt.show()
    plt.close()
    
    return state_metrics

if __name__ == "__main__":
    analyze_center_pressure()
    print("Risk Analysis Complete.")
