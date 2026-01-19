
import pandas as pd
import glob
import os

class AadhaarDataManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.enrolment_path = os.path.join(self.base_dir, "api_data_aadhar_enrolment")
        self.demographic_path = os.path.join(self.base_dir, "api_data_aadhar_demographic")
        self.biometric_path = os.path.join(self.base_dir, "api_data_aadhar_biometric")

    def _load_folder(self, folder_path):
        files = glob.glob(os.path.join(folder_path, "**", "*.csv"), recursive=True)
        if not files:
            return pd.DataFrame()
        df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        # Standardize state column name
        for col in df.columns:
            if col.lower() == "state":
                df.rename(columns={col: "state"}, inplace=True)
                break
        return df

    def get_all_data(self):
        df_enrol = self._load_folder(self.enrolment_path)
        df_demo = self._load_folder(self.demographic_path)
        df_bio = self._load_folder(self.biometric_path)
        
        # Feature Engineering: Totals
        if not df_enrol.empty:
            df_enrol["total_enrolment"] = df_enrol[["age_0_5", "age_5_17", "age_18_greater"]].sum(axis=1)
        
        if not df_demo.empty:
            demo_cols = [c for c in df_demo.select_dtypes(include="number").columns if c not in ["pincode"]]
            df_demo["total_demo_updates"] = df_demo[demo_cols].sum(axis=1)
            
        if not df_bio.empty:
            bio_cols = [c for c in df_bio.select_dtypes(include="number").columns if c not in ["pincode"]]
            df_bio["total_bio_updates"] = df_bio[bio_cols].sum(axis=1)
            
        return df_enrol, df_demo, df_bio

def setup_visuals():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_theme(style="white", palette="muted")
    plt.rcParams["figure.figsize"] = (12, 7)
    plt.rcParams["axes.titlesize"] = 16
    plt.rcParams["axes.labelsize"] = 12
    # Custom color palette for Aadhaar
    return ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B"]
