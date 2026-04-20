from app.analytics.simulator import simulate_cashflow


def analyze_life_event(summary, event_name, one_time_cost=0, monthly_cost_change=0, months=6):
    sim = simulate_cashflow(
        summary=summary,
        income_change=0,
        expense_change=monthly_cost_change,
        months=months,
        one_time_cost=one_time_cost,
    )

    return {
        "event_name": event_name,
        "one_time_cost": one_time_cost,
        "monthly_cost_change": monthly_cost_change,
        "months": months,
        "impact": sim
    }
