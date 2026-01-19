
import subprocess
import os

def run_pipeline():
    print("="*60)
    print("AADHAAR ANALYTICS ENGINE: MASTER RUNNER")
    print("="*60)
    
    scripts = [
        "Analysis_Trends.py",
        "Analysis_Clustering.py",
        "Analysis_Intelligence.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"\n[EXEC] Running {script}...")
            subprocess.run(["python3", script])
        else:
            print(f"\n[WARN] {script} not found.")
            
    print("\n" + "="*60)
    print("PIPELINE COMPLETE. RESULTS IN 'DataVisualisation/'")
    print("SUMMARY IN 'InsightsReport.md'")
    print("To view all graphs at once, run: python3 Show_Results.py")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()