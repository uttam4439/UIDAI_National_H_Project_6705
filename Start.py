
import sys
import os

# Import our modules
from Analysis_Trends import analyze_time_series, analyze_seasonal_bursts, analyze_policy_impact
from Analysis_Clustering import state_clustering_analysis
from Analysis_Intelligence import automation_intelligence
from Analysis_Risk import analyze_center_pressure
from Report_Generator import generate_pdf

def run_pipeline():
    print("="*60)
    print("🚀 INITIALIZING AADHAAR STRATEGIC ANALYSIS PIPELINE")
    print("="*60)
    
    # 1. Run Data Analysis & Generate Visuals
    print("\n[PHASE 1] Data Analysis & Trend Discovery")
    analyze_time_series()
    analyze_seasonal_bursts()
    analyze_policy_impact()
    
    print("\n[PHASE 2] Identity Lifecycle Clustering")
    state_clustering_analysis()
    
    print("\n[PHASE 3] Operational Intelligence & Risk Scoring")
    automation_intelligence()
    analyze_center_pressure()
    
    # 2. Consolidate into PDF
    print("\n[PHASE 4] Report Consolidation")
    generate_pdf()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE: Report generated as Aadhaar_Strategic_Report.pdf")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()