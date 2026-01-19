
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from aadhaar_core import AadhaarDataManager, setup_visuals

colors = setup_visuals()
manager = AadhaarDataManager()
df_enrol, df_demo, df_bio = manager.get_all_data()

def analyze_time_series():
    print("[1/3] Analyzing Time Series & Forecasting...")
    
    # Daily aggregation
    daily_enrol = df_enrol.groupby("date")["total_enrolment"].sum().sort_index()
    
    # Anomaly Detection (Z-score > 2)
    mean = daily_enrol.mean()
    std = daily_enrol.std()
    anomalies = daily_enrol[abs(daily_enrol - mean) > 2 * std]
    
    # Forecasting (ARIMA)
    train = daily_enrol.iloc[:-7] # Leave last 7 days for test if enough data
    if len(train) > 10:
        model = ARIMA(train, order=(1, 1, 1))
        res = model.fit()
        forecast = res.forecast(steps=14)
    else:
        forecast = None

    # Plotting
    plt.figure(figsize=(15, 8))
    plt.plot(daily_enrol.index, daily_enrol.values, marker='o', label="Daily Volume", color=colors[0], alpha=0.6)
    plt.scatter(anomalies.index, anomalies.values, color='red', label="Anomalies (Burst)", zorder=5)
    
    if forecast is not None:
        forecast_idx = pd.date_range(start=daily_enrol.index[-1], periods=15, freq='D')[1:]
        plt.plot(forecast_idx, forecast, '--', color=colors[1], label="14-Day Forecast")
    
    plt.title("Aadhaar Enrolment Trends: Historical with Anomaly Detection & Forecast")
    plt.xlabel("Date")
    plt.ylabel("Total Count")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    save_path = "DataVisualisation/Advanced_Trend_Analysis.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    plt.show() 
    plt.close()

def analyze_seasonal_bursts():
    print("[2/3] Analyzing Seasonal Patterns (Chronological)...")
    
    # Create Year-Month period for chronological sorting
    df_enrol["month_period"] = df_enrol["date"].dt.to_period("M")
    
    # Group by the period and state
    monthly_age = df_enrol.groupby(["month_period", "state"])[["age_0_5", "age_5_17"]].sum().reset_index()
    
    # Format the period back to string for the x-axis (e.g., "Mar 2025")
    monthly_age["month_label"] = monthly_age["month_period"].dt.strftime("%b %Y")
    
    # Sort by the actual period object
    monthly_age = monthly_age.sort_values("month_period")
    
    # Get top 5 states by volume
    top_states = monthly_age.groupby("state")["age_5_17"].sum().nlargest(5).index
    subset = monthly_age[monthly_age["state"].isin(top_states)].copy()
    
    # Ensure the labels keep their chronological order in the plot
    unique_labels = monthly_age["month_label"].unique()
    subset["month_label"] = pd.Categorical(subset["month_label"], categories=unique_labels, ordered=True)

    plt.figure(figsize=(14, 7))
    sns.barplot(data=subset, x="month_label", y="age_5_17", hue="state", palette="viridis")
    plt.title("Student Age (5-17) Aadhaar Activity: Seasonal Peaks (March 2025 onwards)")
    plt.xlabel("Month (Financial/Academic Year Flow)")
    plt.ylabel("Activity Volume")
    plt.xticks(rotation=45)
    
    save_path = "DataVisualisation/Seasonal_Student_Activity.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    
    # Note for user about August
    if "Aug 2025" not in subset["month_label"].unique():
        print("   (!) Note: No enrolment data found for August 2025 in the source datasets.")
        
    plt.show()
    plt.close()

def analyze_policy_impact():
    print("[3/3] Analyzing Policy Interventions...")
    policy_date = pd.to_datetime("2025-07-01")
    
    daily = df_demo.groupby("date")["total_demo_updates"].sum().reset_index()
    before = daily[daily["date"] < policy_date]["total_demo_updates"].mean()
    after = daily[daily["date"] >= policy_date]["total_demo_updates"].mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily["date"], daily["total_demo_updates"], color=colors[2])
    plt.axvline(policy_date, color='black', linestyle='--', label='Policy Intervention')
    plt.fill_between(daily["date"], daily["total_demo_updates"], alpha=0.1, color=colors[2])
    plt.title(f"Policy Impact on Service Usage (Avg Before: {before:.0f} vs After: {after:.0f})")
    plt.legend()
    save_path = "DataVisualisation/Policy_Impact_Analysis.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    plt.show()
    plt.close()

if __name__ == "__main__":
    analyze_time_series()
    analyze_seasonal_bursts()
    analyze_policy_impact()
    print("Trend Analysis Complete.")
