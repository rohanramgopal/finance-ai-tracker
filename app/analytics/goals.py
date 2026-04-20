import math


def evaluate_goals(goals_df):
    if goals_df.empty:
        return []

    result = []
    for _, row in goals_df.iterrows():
        remaining = max(0, row["target_amount"] - row["current_amount"])
        monthly = row["monthly_contribution"]

        if monthly <= 0:
            projected_months = 9999
            status = "Off Track"
        else:
            projected_months = math.ceil(remaining / monthly) if remaining > 0 else 0
            status = "Completed" if remaining == 0 else "On Track"

        result.append({
            "name": row["name"],
            "target_amount": float(row["target_amount"]),
            "current_amount": float(row["current_amount"]),
            "monthly_contribution": float(row["monthly_contribution"]),
            "projected_months": int(projected_months),
            "status": status,
        })
    return result
