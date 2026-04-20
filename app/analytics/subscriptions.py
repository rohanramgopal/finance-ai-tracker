KEYWORDS = ["netflix", "spotify", "prime", "hotstar", "subscription", "youtube", "apple", "google one"]


def detect_subscriptions(df):
    expense_df = df[df["type"] == "Expense"].copy()
    if expense_df.empty:
        return {"subscriptions": [], "monthly_burden": 0.0, "annualized_burden": 0.0}

    expense_df["desc_lower"] = expense_df["description"].astype(str).str.lower()

    subs = expense_df[
        expense_df["desc_lower"].apply(lambda x: any(k in x for k in KEYWORDS))
    ].copy()

    if subs.empty:
        return {"subscriptions": [], "monthly_burden": 0.0, "annualized_burden": 0.0}

    grouped = subs.groupby("description")["amount"].mean().sort_values(ascending=False)
    subscriptions = [{"merchant": idx, "estimated_monthly_cost": float(val)} for idx, val in grouped.items()]
    monthly_burden = float(grouped.sum())

    return {
        "subscriptions": subscriptions,
        "monthly_burden": monthly_burden,
        "annualized_burden": monthly_burden * 12
    }
