def simulate_cashflow(summary, income_change=0, expense_change=0, emi_change=0, rent_change=0, months=6, one_time_cost=0):
    current_income = float(summary["total_income"])
    current_expense = float(summary["total_expense"])

    monthly_income = current_income + income_change
    monthly_expense = current_expense + expense_change + emi_change + rent_change

    balance = 0 - one_time_cost
    timeline = []

    for month in range(1, months + 1):
        monthly_saving = monthly_income - monthly_expense
        balance += monthly_saving
        timeline.append({
            "month": month,
            "projected_income": monthly_income,
            "projected_expense": monthly_expense,
            "monthly_saving": monthly_saving,
            "cumulative_balance": balance,
        })

    resilience = "Stable"
    if balance < 0:
        resilience = "At Risk"
    if any(item["monthly_saving"] < 0 for item in timeline):
        resilience = "Unstable"

    return {
        "timeline": timeline,
        "resilience": resilience,
        "final_balance": balance
    }
