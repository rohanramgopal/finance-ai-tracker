def build_risk_radar(df, summary):
    income = float(summary.get("total_income", 0) or 0)
    expense = float(summary.get("total_expense", 0) or 0)
    savings = float(summary.get("savings", 0) or 0)

    risks = []

    if income <= 0:
        risks.append({
            "name": "Income Risk",
            "level": "High",
            "reason": "No income detected.",
            "action": "Add income entries or verify salary tracking."
        })
    else:
        savings_rate = (savings / income) * 100 if income else 0

        if savings_rate < 10:
            risks.append({
                "name": "Savings Risk",
                "level": "High",
                "reason": "Savings rate is below 10%.",
                "action": "Reduce discretionary expenses and lock a fixed monthly saving amount."
            })
        elif savings_rate < 20:
            risks.append({
                "name": "Savings Risk",
                "level": "Medium",
                "reason": "Savings rate is below the ideal range.",
                "action": "Review your largest expense category."
            })
        else:
            risks.append({
                "name": "Savings Risk",
                "level": "Low",
                "reason": "Savings rate is healthy.",
                "action": "Maintain the current trend."
            })

    expense_df = df[df["type"] == "Expense"].copy()
    if not expense_df.empty and expense > 0:
        grouped = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_category = grouped.index[0]
        top_amount = float(grouped.iloc[0])
        share = (top_amount / expense) * 100

        if share > 40:
            risks.append({
                "name": "Category Concentration Risk",
                "level": "High",
                "reason": f"{top_category} forms {share:.1f}% of total expenses.",
                "action": f"Reduce or cap {top_category} spending."
            })
        elif share > 25:
            risks.append({
                "name": "Category Concentration Risk",
                "level": "Medium",
                "reason": f"{top_category} is your dominant expense category.",
                "action": f"Track {top_category} weekly."
            })
        else:
            risks.append({
                "name": "Category Concentration Risk",
                "level": "Low",
                "reason": "No single category is dominating your cashflow.",
                "action": "Keep monitoring category distribution."
            })

    if savings < 0:
        risks.append({
            "name": "Cashflow Stability Risk",
            "level": "High",
            "reason": "Current cashflow is negative.",
            "action": "Cut variable expenses immediately or increase income."
        })
    elif savings == 0:
        risks.append({
            "name": "Cashflow Stability Risk",
            "level": "Medium",
            "reason": "There is no monthly savings buffer.",
            "action": "Create a baseline monthly surplus."
        })
    else:
        risks.append({
            "name": "Cashflow Stability Risk",
            "level": "Low",
            "reason": "Current cashflow is positive.",
            "action": "Continue building resilience."
        })

    return risks
