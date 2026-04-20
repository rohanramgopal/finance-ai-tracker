import streamlit as st
import plotly.express as px

from utils.helpers import (
    load_data,
    monthly_summary,
    category_expense_breakdown,
    monthly_trend,
    initialize_data_file,
)
from utils.insights import financial_health_score
from utils.anomaly import detect_anomalies

st.set_page_config(page_title="Personal Finance AI Tracker", page_icon="💸", layout="wide")

initialize_data_file()
df = load_data()

st.title("💸 Personal Finance AI Tracker")
st.caption("Track income, expenses, budgets, anomalies, and AI-powered financial insights.")

summary = monthly_summary(df)
health_score = financial_health_score(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{summary['income']:,.2f}")
col2.metric("Total Expenses", f"₹{summary['expense']:,.2f}")
col3.metric("Savings", f"₹{summary['savings']:,.2f}")
col4.metric("Health Score", f"{health_score}/100")

st.markdown("---")

if df.empty:
    st.warning("No transactions found. Add transactions from the sidebar pages.")
else:
    left, right = st.columns(2)

    with left:
        st.subheader("Category-wise Expense Breakdown")
        cat_df = category_expense_breakdown(df)
        if not cat_df.empty:
            fig_pie = px.pie(cat_df, names="category", values="amount", hole=0.45)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data available.")

    with right:
        st.subheader("Monthly Expense Trend")
        trend_df = monthly_trend(df)
        if not trend_df.empty:
            fig_line = px.line(trend_df, x="month", y="amount", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Not enough trend data.")

    st.markdown("---")

    st.subheader("Recent Transactions")
    display_df = df.sort_values(by="date", ascending=False).copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True)

    st.markdown("---")

    st.subheader("Anomaly Detection")
    anomalies = detect_anomalies(df)
    if anomalies.empty:
        st.success("No unusual expense transactions detected.")
    else:
        anomaly_view = anomalies[["date", "category", "amount", "description", "payment_mode"]].copy()
        anomaly_view["date"] = anomaly_view["date"].dt.strftime("%Y-%m-%d")
        st.warning("Unusual transactions detected:")
        st.dataframe(anomaly_view, use_container_width=True)