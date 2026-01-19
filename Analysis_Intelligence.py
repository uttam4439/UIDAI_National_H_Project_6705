
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from aadhaar_core import AadhaarDataManager, setup_visuals

colors = setup_visuals()
manager = AadhaarDataManager()
_, df_demo, _ = manager.get_all_data()

def automation_intelligence():
    print("[1/1] Processing Rejection Patterns & Automation Intelligence...")
    
    if "change_reason" not in df_demo.columns:
        print(f"Skipping NLP: 'change_reason' column not found in dataset.")
        print(f"Available columns: {df_demo.columns.tolist()}")
        return

    df = df_demo.copy().dropna(subset=["change_reason"])
    df["change_reason"] = df["change_reason"].fillna("").astype(str)
    
    # Simple logic to create labels if missing
    def proxy_status(text):
        if any(msg in text.lower() for msg in ["invalid", "wrong", "error", "@", "bad"]):
            return 1 # Manual/Rejected
        return 0 # Approved
        
    df["manual_flag"] = df["change_reason"].apply(proxy_status)
    
    # Vectorization
    vectorizer = TfidfVectorizer(max_features=100)
    X = vectorizer.fit_transform(df["change_reason"])
    y = df["manual_flag"]
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Feature Importance
    features = vectorizer.get_feature_names_out()
    importance = model.coef_[0]
    feat_df = pd.DataFrame({"Feature": features, "Weight": importance}).sort_values("Weight", ascending=False)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=feat_df.head(10), x="Weight", y="Feature", color=colors[3])
    plt.title("Keywords Driving Rejection & Manual Review Necessity")
    save_path = "DataVisualisation/Intelligence_Rejection_Drivers.png"
    plt.savefig(save_path, dpi=300)
    print(f"   -> Visualization saved to: {save_path}")
    plt.show()
    plt.close()

if __name__ == "__main__":
    automation_intelligence()
