import streamlit as st
from datetime import date

from utils.helpers import save_transaction, rule_based_category, load_data

st.set_page_config(page_title="Add Transaction", page_icon="➕", layout="wide")

st.title("➕ Add Transaction")

with st.form("transaction_form", clear_on_submit=True):
    trans_date = st.date_input("Date", value=date.today())
    trans_type = st.selectbox("Type", ["Expense", "Income"])
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    description = st.text_input("Description", placeholder="e.g. Swiggy order, Salary credited")
    payment_mode = st.selectbox("Payment Mode", ["UPI", "Card", "Cash", "Bank Transfer", "Wallet"])
    manual_category = st.text_input("Category (optional)", placeholder="Leave blank for auto-category")

    submitted = st.form_submit_button("Save Transaction")

if submitted:
    if amount <= 0:
        st.error("Amount must be greater than 0.")
    elif not description.strip():
        st.error("Description is required.")
    else:
        category = manual_category.strip() if manual_category.strip() else rule_based_category(description, trans_type)

        save_transaction(
            date_value=trans_date,
            trans_type=trans_type,
            category=category,
            amount=amount,
            description=description,
            payment_mode=payment_mode,
        )

        st.success(f"Transaction saved successfully under category: {category}")

        latest_df = load_data()
        st.subheader("Latest Saved Transactions")
        st.dataframe(latest_df.sort_values(by="date", ascending=False), use_container_width=True)

        st.rerun()