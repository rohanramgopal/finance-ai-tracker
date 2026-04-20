import streamlit as st
import pandas as pd

from utils.helpers import load_data, category_expense_breakdown

st.set_page_config(page_title="Budget Planner", page_icon="📊", layout="wide")

st.title("📊 Budget Planner")

df = load_data()

if df.empty:
    st.warning("No data found. Please add transactions first.")
    st.stop()

st.write("Set your budgets and compare with actual spending.")

default_budgets = {
    "Food": 5000,
    "Transport": 3000,
    "Shopping": 4000,
    "Bills": 6000,
    "Entertainment": 2000,
    "Health": 3000,
    "Travel": 5000,
    "Education": 4000,
    "Other": 2000,
}

st.subheader("Set Budgets")

budgets = {}
cols = st.columns(3)

for i, category in enumerate(default_budgets.keys()):
    with cols[i % 3]:
        budgets[category] = st.number_input(
            f"{category}",
            min_value=0,
            value=default_budgets[category],
            step=500,
        )

st.markdown("---")

expense_df = category_expense_breakdown(df)

st.subheader("Budget vs Actual")

rows = []

for category in default_budgets.keys():
    actual = 0

    if not expense_df.empty and category in expense_df["category"].values:
        actual = float(expense_df.loc[expense_df["category"] == category, "amount"].values[0])

    budget = budgets[category]
    remaining = budget - actual

    rows.append(
        {
            "Category": category,
            "Budget": budget,
            "Actual": actual,
            "Remaining": remaining,
            "Status": "✅ OK" if actual <= budget else "❌ Over Budget",
        }
    )

result_df = pd.DataFrame(rows)

st.dataframe(result_df, use_container_width=True)

over = result_df[result_df["Status"] == "❌ Over Budget"]

if not over.empty:
    st.error("You are over budget in some categories.")
    st.dataframe(over, use_container_width=True)
else:
    st.success("All categories are within budget.")