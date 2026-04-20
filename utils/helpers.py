import os
import pandas as pd

DATA_FILE = "data/transactions.csv"

DEFAULT_COLUMNS = [
    "date",
    "type",
    "category",
    "amount",
    "description",
    "payment_mode",
]


def initialize_data_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=DEFAULT_COLUMNS)
        df.to_csv(DATA_FILE, index=False)


def load_data():
    initialize_data_file()

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=DEFAULT_COLUMNS)

    if df.empty:
        return pd.DataFrame(columns=DEFAULT_COLUMNS)

    for col in DEFAULT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    return df


def save_transaction(date_value, trans_type, category, amount, description, payment_mode):
    initialize_data_file()

    new_row = pd.DataFrame(
        [
            {
                "date": pd.to_datetime(date_value).strftime("%Y-%m-%d"),
                "type": trans_type,
                "category": category,
                "amount": float(amount),
                "description": str(description),
                "payment_mode": str(payment_mode),
            }
        ]
    )

    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        new_row.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else:
        new_row.to_csv(DATA_FILE, mode="w", header=True, index=False)


def rule_based_category(description, trans_type):
    desc = str(description).lower().strip()

    if trans_type == "Income":
        if any(word in desc for word in ["salary", "credited", "income", "bonus", "freelance", "payment"]):
            return "Salary"
        return "Income"

    keyword_map = {
        "Food": ["swiggy", "zomato", "restaurant", "cafe", "food", "dinner", "lunch", "breakfast"],
        "Transport": ["uber", "ola", "bus", "metro", "petrol", "fuel", "auto", "taxi", "transport"],
        "Shopping": ["amazon", "flipkart", "myntra", "shopping", "order"],
        "Bills": ["electricity", "water", "rent", "internet", "bill", "recharge"],
        "Entertainment": ["netflix", "spotify", "movie", "prime", "hotstar", "game"],
        "Health": ["hospital", "pharmacy", "doctor", "medicine", "health"],
        "Travel": ["flight", "hotel", "trip", "train", "travel", "booking"],
        "Education": ["course", "udemy", "book", "exam", "fees", "tuition"],
    }

    for category, words in keyword_map.items():
        if any(word in desc for word in words):
            return category

    return "Other"


def monthly_summary(df):
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "savings": 0.0}

    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()
    savings = income - expense

    return {
        "income": float(income),
        "expense": float(expense),
        "savings": float(savings),
    }


def category_expense_breakdown(df):
    if df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    expense_df = df[df["type"] == "Expense"].copy()

    if expense_df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    result = (
        expense_df.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values(by="amount", ascending=False)
    )

    return result


def monthly_trend(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "amount"])

    expense_df = df[df["type"] == "Expense"].copy()

    if expense_df.empty:
        return pd.DataFrame(columns=["month", "amount"])

    expense_df["month"] = expense_df["date"].dt.to_period("M").astype(str)
    trend = expense_df.groupby("month", as_index=False)["amount"].sum()

    return trend