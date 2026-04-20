import pandas as pd


def generate_insights(df):
    insights = []

    if df.empty:
        return ["No transaction data available yet. Add some transactions to generate insights."]

    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()

    if income > 0:
        savings_rate = ((income - expense) / income) * 100
        insights.append(f"Your current savings rate is {savings_rate:.1f}%.")

        if savings_rate < 20:
            insights.append("Your savings rate is below 20%. Consider reducing non-essential spending.")
        else:
            insights.append("Your savings rate looks healthy.")

    expense_df = df[df["type"] == "Expense"].copy()

    if not expense_df.empty:
        category_spend = (
            expense_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        top_category = category_spend.index[0]
        top_amount = category_spend.iloc[0]
        insights.append(f"Your top spending category is {top_category} at ₹{top_amount:.2f}.")

        if len(category_spend) > 1:
            second_category = category_spend.index[1]
            insights.append(f"The next biggest spending category is {second_category}.")

        expense_df["month"] = expense_df["date"].dt.to_period("M")
        month_summary = expense_df.groupby("month")["amount"].sum().sort_index()

        if len(month_summary) >= 2:
            prev_month = month_summary.iloc[-2]
            curr_month = month_summary.iloc[-1]

            if prev_month > 0:
                change = ((curr_month - prev_month) / prev_month) * 100
                if change > 0:
                    insights.append(f"Your expenses increased by {change:.1f}% compared to the previous month.")
                elif change < 0:
                    insights.append(f"Your expenses decreased by {abs(change):.1f}% compared to the previous month.")
                else:
                    insights.append("Your spending is unchanged compared to the previous month.")

    return insights


def financial_health_score(df):
    if df.empty:
        return 50

    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()

    if income <= 0:
        return 40

    savings_rate = ((income - expense) / income) * 100
    score = 50

    if savings_rate >= 40:
        score += 35
    elif savings_rate >= 20:
        score += 25
    elif savings_rate >= 10:
        score += 15
    else:
        score += 5

    expense_df = df[df["type"] == "Expense"]
    unique_categories = expense_df["category"].nunique() if not expense_df.empty else 0

    if unique_categories >= 4:
        score += 10

    if expense > income:
        score -= 20

    score = max(0, min(100, score))
    return score