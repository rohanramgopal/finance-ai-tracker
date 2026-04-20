import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from app.db.models import Transaction, Goal

CANONICAL_CATEGORIES = {
    "food": "Food",
    "transport": "Transport",
    "shopping": "Shopping",
    "bills": "Bills",
    "entertainment": "Entertainment",
    "health": "Health",
    "travel": "Travel",
    "education": "Education",
    "other": "Other",
    "salary": "Salary",
    "income": "Income",
}


def normalize_category(category: str, tx_type: str = "") -> str:
    if category is None:
        category = ""

    raw = str(category).strip()
    if not raw:
        return "Salary" if tx_type == "Income" else "Other"

    key = raw.lower()
    if key in CANONICAL_CATEGORIES:
        return CANONICAL_CATEGORIES[key]

    return raw[:1].upper() + raw[1:].lower()


def rule_based_category(description, type_):
    desc = str(description).lower().strip()

    if type_ == "Income":
        if any(word in desc for word in ["salary", "credited", "income", "bonus", "freelance", "payment"]):
            return "Salary"
        return "Income"

    keyword_map = {
        "Food": ["swiggy", "zomato", "restaurant", "cafe", "food", "dinner", "lunch", "breakfast"],
        "Transport": ["uber", "ola", "bus", "metro", "petrol", "fuel", "auto", "taxi", "transport"],
        "Shopping": ["amazon", "flipkart", "myntra", "shopping", "order"],
        "Bills": ["electricity", "water", "rent", "internet", "bill", "recharge"],
        "Entertainment": ["netflix", "spotify", "movie", "prime", "hotstar", "game", "subscription"],
        "Health": ["hospital", "pharmacy", "doctor", "medicine", "health"],
        "Travel": ["flight", "hotel", "trip", "train", "travel", "booking"],
        "Education": ["course", "udemy", "book", "exam", "fees", "tuition"],
    }

    for category, words in keyword_map.items():
        if any(word in desc for word in words):
            return category

    return "Other"


def load_data_from_db(db: Session):
    rows = db.query(Transaction).order_by(Transaction.id.asc()).all()
    if not rows:
        return pd.DataFrame(columns=["id", "date", "type", "category", "amount", "description", "payment_mode"])

    df = pd.DataFrame([
        {
            "id": row.id,
            "date": row.date,
            "type": row.type,
            "category": row.category,
            "amount": row.amount,
            "description": row.description,
            "payment_mode": row.payment_mode,
        }
        for row in rows
    ])

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["category"] = df.apply(lambda r: normalize_category(r["category"], r["type"]), axis=1)

    return df


def load_goals_from_db(db: Session):
    rows = db.query(Goal).order_by(Goal.id.asc()).all()
    if not rows:
        return pd.DataFrame(columns=["name", "target_amount", "current_amount", "monthly_contribution", "target_date"])

    return pd.DataFrame([
        {
            "name": row.name,
            "target_amount": row.target_amount,
            "current_amount": row.current_amount,
            "monthly_contribution": row.monthly_contribution,
            "target_date": row.target_date,
        }
        for row in rows
    ])


def get_summary(df):
    if df.empty:
        return {"total_income": 0.0, "total_expense": 0.0, "savings": 0.0}

    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()

    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "savings": float(income - expense),
    }


def get_insights(df):
    if df.empty:
        return {"insights": ["No transaction data available yet."], "health_score": 50}

    insights = []
    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()

    if income > 0:
        savings_rate = ((income - expense) / income) * 100
        insights.append(f"Your current savings rate is {savings_rate:.1f}%.")

    expense_df = df[df["type"] == "Expense"].copy()
    if not expense_df.empty:
        grouped = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_category = grouped.index[0]
        top_amount = grouped.iloc[0]
        insights.append(f"Your highest spending category is {top_category} at ₹{top_amount:.2f}.")

    health_score = 40
    if income > 0:
        savings_rate = ((income - expense) / income) * 100
        if savings_rate >= 40:
            health_score = 85
        elif savings_rate >= 20:
            health_score = 75
        elif savings_rate >= 10:
            health_score = 65
        else:
            health_score = 50

    return {"insights": insights, "health_score": health_score}


def get_budget_vs_actual(df):
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

    expense_df = df[df["type"] == "Expense"].copy()
    grouped = expense_df.groupby("category")["amount"].sum().to_dict() if not expense_df.empty else {}

    result = []
    for category, budget in default_budgets.items():
        actual = float(grouped.get(category, 0))
        remaining = budget - actual
        status = "Over Budget" if actual > budget else "OK"

        result.append({
            "category": category,
            "budget": budget,
            "actual": actual,
            "remaining": remaining,
            "status": status,
        })

    return result


def detect_anomalies(df):
    if df.empty:
        return []

    expense_df = df[df["type"] == "Expense"].copy()
    if expense_df.empty or len(expense_df) < 5:
        return []

    model = IsolationForest(contamination=0.15, random_state=42)
    expense_df["anomaly"] = model.fit_predict(expense_df[["amount"]])

    anomalies = expense_df[expense_df["anomaly"] == -1].copy()
    if anomalies.empty:
        return []

    anomalies["date"] = anomalies["date"].astype(str)
    rows = anomalies[["id", "date", "type", "category", "amount", "description", "payment_mode"]].to_dict(orient="records")

    cleaned = []
    for row in rows:
        cleaned.append(
            {
                "id": int(row.get("id", 0)),
                "date": str(row.get("date", ""))[:10],
                "type": str(row.get("type", "")),
                "category": normalize_category(row.get("category", ""), row.get("type", "")),
                "amount": float(row.get("amount", 0) or 0),
                "description": str(row.get("description", "")),
                "payment_mode": str(row.get("payment_mode", "")),
            }
        )

    return cleaned
