def explain_health(df, summary):
    reasons_positive = []
    reasons_negative = []

    income = summary["total_income"]
    expense = summary["total_expense"]
    savings = summary["savings"]

    if income > 0:
        savings_rate = (savings / income) * 100
    else:
        savings_rate = 0

    score = 50

    if savings_rate >= 40:
        score += 30
        reasons_positive.append("Strong savings rate above 40%.")
    elif savings_rate >= 20:
        score += 20
        reasons_positive.append("Healthy savings rate above 20%.")
    elif savings_rate < 10:
        score -= 10
        reasons_negative.append("Savings rate is below 10%.")

    expense_df = df[df["type"] == "Expense"].copy()
    top_category = None
    if not expense_df.empty:
        grouped = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_category = grouped.index[0]
        top_amount = grouped.iloc[0]
        if income > 0 and (top_amount / income) > 0.35:
            score -= 10
            reasons_negative.append(f"{top_category} takes a large share of income.")

    if savings > 0:
        reasons_positive.append("Cashflow is still positive after expenses.")
    else:
        reasons_negative.append("Expenses are eroding savings.")

    score = max(0, min(100, score))

    return {
        "score": score,
        "positive_factors": reasons_positive,
        "negative_factors": reasons_negative,
        "best_improvement_action": f"Reduce {top_category} spending first." if top_category else "Add more transaction history."
    }
