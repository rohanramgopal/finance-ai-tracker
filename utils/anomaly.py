import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df):
    if df.empty:
        return pd.DataFrame()

    expense_df = df[df["type"] == "Expense"].copy()

    if expense_df.empty:
        return pd.DataFrame()

    if len(expense_df) < 5:
        return pd.DataFrame()

    model = IsolationForest(contamination=0.15, random_state=42)
    expense_df["anomaly"] = model.fit_predict(expense_df[["amount"]])

    return expense_df[expense_df["anomaly"] == -1]