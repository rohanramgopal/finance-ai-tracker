def build_spending_persona(df):
    expense_df = df[df["type"] == "Expense"].copy()
    if expense_df.empty:
        return {
            "persona": "Insufficient Data",
            "traits": [],
            "risks": [],
            "recommendations": ["Add more expense history to build a spending profile."]
        }

    expense_df["weekday"] = expense_df["date"].dt.day_name()
    expense_df["day"] = expense_df["date"].dt.day
    total = expense_df["amount"].sum()

    grouped = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_category = grouped.index[0]
    top_share = grouped.iloc[0] / total if total else 0

    weekend_spend = expense_df[expense_df["weekday"].isin(["Saturday", "Sunday"])]["amount"].sum()
    weekend_share = weekend_spend / total if total else 0

    early_month_spend = expense_df[expense_df["day"] <= 10]["amount"].sum()
    early_month_share = early_month_spend / total if total else 0

    persona = "Balanced Planner"
    traits = []
    risks = []
    recommendations = []

    if top_share > 0.45:
        persona = "Category Concentrated Spender"
        traits.append(f"Spending is highly concentrated in {top_category}.")
        risks.append("Budget shock risk from one dominant category.")
        recommendations.append(f"Cap {top_category} with a tighter monthly budget.")

    if weekend_share > 0.35:
        persona = "Weekend Spike Spender"
        traits.append("A large share of spending happens on weekends.")
        risks.append("Impulse purchases may be clustered on weekends.")
        recommendations.append("Set a separate weekend discretionary cap.")

    if early_month_share > 0.55:
        persona = "Salary-Week Spender"
        traits.append("Most money is spent early in the month.")
        risks.append("Late-month cash compression risk.")
        recommendations.append("Distribute spending targets across all four weeks.")

    if not recommendations:
        recommendations.append("Maintain current habits and review biggest category monthly.")

    return {
        "persona": persona,
        "traits": traits,
        "risks": risks,
        "recommendations": recommendations
    }
