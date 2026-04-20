import streamlit as st

from utils.helpers import load_data
from utils.insights import generate_insights, financial_health_score

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")

st.title("🤖 AI Financial Insights")

df = load_data()
insights = generate_insights(df)
score = financial_health_score(df)

st.subheader("Financial Health Score")
st.progress(score / 100)
st.write(f"Your score is **{score}/100**")

st.markdown("---")
st.subheader("Smart Insights")

for insight in insights:
    st.info(insight)

st.markdown("---")
st.subheader("Ask for Suggestions")

question = st.text_input(
    "Ask something about your finances",
    placeholder="e.g. Where am I spending the most? How can I save more?"
)

if question:
    q = question.lower()

    income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
    expense_df = df[df["type"] == "Expense"].copy()

    if "spending the most" in q or "where am i spending" in q or "highest spending" in q:
        if expense_df.empty:
            st.warning("No expense data available yet.")
        else:
            category_spend = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            top_category = category_spend.index[0]
            top_amount = category_spend.iloc[0]
            st.success(f"You are spending the most on **{top_category}**: ₹{top_amount:.2f}")

    elif "save more" in q or "how can i save" in q:
        if expense_df.empty:
            st.warning("Add some expense data first.")
        else:
            category_spend = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            top_category = category_spend.index[0]
            st.success(
                f"To save more, start by reducing **{top_category}** expenses, because that is your biggest spending area."
            )

    elif "savings" in q:
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0
        savings = income - expense
        st.success(f"Your current total savings are **₹{savings:.2f}**")

    elif "food" in q:
        food_spend = expense_df[expense_df["category"] == "Food"]["amount"].sum() if not expense_df.empty else 0
        st.success(f"You have spent **₹{food_spend:.2f}** on Food.")

    else:
        st.info("Try asking: 'Where am I spending the most?', 'How can I save more?', or 'What are my savings?'")