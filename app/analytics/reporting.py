from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def create_cfo_report(path, summary, insights, persona, subscriptions):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, y, "Monthly CFO Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 30

    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Executive Summary")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Income: ₹{summary['total_income']:.2f}")
    y -= 18
    c.drawString(40, y, f"Expense: ₹{summary['total_expense']:.2f}")
    y -= 18
    c.drawString(40, y, f"Savings: ₹{summary['savings']:.2f}")
    y -= 28

    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Top Insights")
    y -= 20
    c.setFont("Helvetica", 11)
    for item in insights[:4]:
        c.drawString(50, y, f"- {item}")
        y -= 18

    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Spending Persona")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Persona: {persona.get('persona', 'N/A')}")
    y -= 25

    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Subscriptions")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Monthly Burden: ₹{subscriptions.get('monthly_burden', 0):.2f}")
    y -= 18
    c.drawString(40, y, f"Annualized Burden: ₹{subscriptions.get('annualized_burden', 0):.2f}")

    c.save()
    return path
