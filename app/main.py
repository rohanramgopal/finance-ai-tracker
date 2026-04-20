from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import Base, engine, get_db
from app.routes.auth import router as auth_router
from app.routes.transactions import router as transactions_router
from app.schemas import GoalCreate, ScenarioInput
from app.db.models import Goal
from app import services
from app.analytics.persona import build_spending_persona
from app.analytics.subscriptions import detect_subscriptions
from app.analytics.goals import evaluate_goals
from app.analytics.simulator import simulate_cashflow
from app.analytics.reporting import create_cfo_report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance AI Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transactions_router)


@app.get("/")
def root():
    return {"message": "API running. Go to /docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return services.get_summary(df)


@app.get("/insights")
def insights(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return services.get_insights(df)


@app.get("/budgets")
def budgets(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return services.get_budget_vs_actual(df)


@app.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return services.detect_anomalies(df)


@app.get("/spending-dna")
def spending_dna(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return build_spending_persona(df)


@app.get("/subscriptions")
def subscriptions(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    return detect_subscriptions(df)


@app.post("/goals")
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    row = Goal(
        name=goal.name.strip(),
        target_amount=float(goal.target_amount),
        current_amount=float(goal.current_amount),
        monthly_contribution=float(goal.monthly_contribution),
        target_date=goal.target_date or "",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"message": "Goal saved successfully"}


@app.get("/goals")
def goals(db: Session = Depends(get_db)):
    goals_df = services.load_goals_from_db(db)
    return evaluate_goals(goals_df)


@app.post("/simulate")
def simulate(payload: ScenarioInput, db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    summary = services.get_summary(df)
    return simulate_cashflow(
        summary=summary,
        income_change=payload.income_change,
        expense_change=payload.expense_change,
        emi_change=payload.emi_change,
        rent_change=payload.rent_change,
        months=payload.months,
        one_time_cost=payload.one_time_cost,
    )


@app.get("/why-expense-change")
def why_expense_change(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    expense_df = df[df["type"] == "Expense"].copy()

    if expense_df.empty or len(expense_df) < 2:
        return {"answer": "Not enough data to analyze change."}

    expense_df = expense_df.sort_values("date")
    mid = len(expense_df) // 2
    first = expense_df.iloc[:mid]
    second = expense_df.iloc[mid:]

    first_total = first["amount"].sum()
    second_total = second["amount"].sum()

    if first_total == 0:
        return {"answer": "No baseline data to compare."}

    change = ((second_total - first_total) / first_total) * 100
    top = second.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_cat = top.index[0]
    top_amt = top.iloc[0]

    return {
        "answer": f"Expenses changed by {change:.1f}%. Major driver: {top_cat} (₹{top_amt:.0f})."
    }


@app.get("/report")
def report(db: Session = Depends(get_db)):
    df = services.load_data_from_db(db)
    summary = services.get_summary(df)
    insights = services.get_insights(df)["insights"]
    persona = build_spending_persona(df)
    subscriptions = detect_subscriptions(df)

    path = "monthly_cfo_report.pdf"
    create_cfo_report(path, summary, insights, persona, subscriptions)
    return FileResponse(path, media_type="application/pdf", filename="monthly_cfo_report.pdf")
