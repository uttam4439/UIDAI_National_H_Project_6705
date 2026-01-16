import pandas as pd
import numpy as np
import glob
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
demographic_path = os.path.join(BASE_DIR, "api_data_aadhar_demographic")

files = glob.glob(os.path.join(demographic_path, "**", "*.csv"), recursive=True)

if not files:
    raise ValueError("No demographic files found")

df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

print("Dataset loaded:", df.shape)
print(df.columns)

# Standardize column names
df.columns = df.columns.str.lower()

# Fill missing text fields safely
text_cols = ["remarks", "rejection_reason", "change_reason"]
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna("")

def pre_validation(row):
    if "@" in row.get("change_reason", ""):
        return "REJECT_INVALID"
    if len(row.get("change_reason", "")) < 2:
        return "REJECT_INCOMPLETE"
    return "PASS"

df["pre_validation_status"] = df.apply(pre_validation, axis=1)

def auto_approval_rules(row):
    if row.get("failure_count", 0) == 0 and len(row.get("change_reason", "")) < 25:
        return "AUTO_APPROVE"
    return "REVIEW"

df["rule_decision"] = df.apply(auto_approval_rules, axis=1)

# If final_status exists, use it
if "final_status" in df.columns:
    df["manual_required"] = df["final_status"].apply(
        lambda x: 0 if x == "APPROVED" else 1
    )
else:
    # Fallback proxy label
    df["manual_required"] = df["rule_decision"].apply(
        lambda x: 0 if x == "AUTO_APPROVE" else 1
    )

vectorizer = TfidfVectorizer(
    max_features=300,
    stop_words="english"
)

X_text = vectorizer.fit_transform(df["change_reason"])
y = df["manual_required"]

X_train, X_test, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))

def find_duplicates(text_series, threshold=0.85):
    tfidf = vectorizer.fit_transform(text_series)
    similarity_matrix = cosine_similarity(tfidf)

    duplicates = []
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i, j] > threshold:
                duplicates.append((i, j))
    return duplicates

duplicate_pairs = find_duplicates(df["change_reason"])
print("Potential duplicate requests:", duplicate_pairs[:5])

def final_decision(row):
    if row["pre_validation_status"] != "PASS":
        return "REJECT"
    if row["rule_decision"] == "AUTO_APPROVE":
        return "AUTO_APPROVED"
    if row["manual_required"] == 0:
        return "AUTO_APPROVED"
    return "MANUAL_REVIEW"

df["final_decision"] = df.apply(final_decision, axis=1)

print(df["final_decision"].value_counts())
