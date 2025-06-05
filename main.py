from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI()

class UnderwriteRequest(BaseModel):
    url: str
    adr: float
    occupancy: float
    roi_target: float
    down_payment_pct: float
    interest_rate: float
    loan_term: int
    expense_pct: float
    purchase_price: float

def calculate_mortgage(principal, rate, years):
    r = rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

@app.post("/api/underwrite")
def underwrite(data: UnderwriteRequest):
    # Income
    gross_income = data.adr * (data.occupancy / 100) * 365
    expenses = gross_income * (data.expense_pct / 100)
    noi = gross_income - expenses

    # Financing
    down_payment = data.purchase_price * (data.down_payment_pct / 100)
    loan_amount = data.purchase_price - down_payment
    monthly_pi = calculate_mortgage(loan_amount, data.interest_rate, data.loan_term)

    # Returns
    annual_pi = monthly_pi * 12
    cap_rate = (noi / data.purchase_price) * 100
    annual_cash_flow = noi - annual_pi
    monthly_cash_flow = annual_cash_flow / 12
    coc_return = (annual_cash_flow / down_payment) * 100

    # Optimizations (example logic: improve by 5-10% margins)
    optimized = {
        "adr": round(data.adr * 1.10, 2),
        "occupancy": round(min(data.occupancy * 1.10, 100), 2),
        "price_discount": 0.95,
    }

    opt_gross = optimized["adr"] * (optimized["occupancy"] / 100) * 365
    opt_exp = opt_gross * (data.expense_pct / 100)
    opt_noi = opt_gross - opt_exp
    opt_price = data.purchase_price * optimized["price_discount"]
    opt_loan = opt_price - (opt_price * (data.down_payment_pct / 100))
    opt_monthly_pi = calculate_mortgage(opt_loan, data.interest_rate, data.loan_term)
    opt_annual_pi = opt_monthly_pi * 12
    opt_cash_flow = opt_noi - opt_annual_pi
    opt_coc = (opt_cash_flow / (opt_price * (data.down_payment_pct / 100))) * 100

    return {
        "original_inputs": {
            "Zillow URL": data.url,
            "ADR": data.adr,
            "Occupancy": data.occupancy,
            "Target ROI": data.roi_target,
            "Down Payment %": data.down_payment_pct,
            "Interest Rate %": data.interest_rate,
            "Loan Term": data.loan_term,
            "Expenses %": data.expense_pct,
            "Purchase Price": data.purchase_price
        },
        "results": {
            "Gross Annual Income": round(gross_income, 2),
            "NOI": round(noi, 2),
            "Cap Rate %": round(cap_rate, 2),
            "Monthly P&I": round(monthly_pi, 2),
            "Monthly Cash Flow": round(monthly_cash_flow, 2),
            "Cash-on-Cash Return %": round(coc_return, 2)
        },
        "optimized": {
            "ADR": optimized["adr"],
            "Occupancy": optimized["occupancy"],
            "Discounted Price": round(opt_price, 2),
            "NOI": round(opt_noi, 2),
            "Monthly P&I": round(opt_monthly_pi, 2),
            "Monthly Cash Flow": round(opt_cash_flow / 12, 2),
            "Cash-on-Cash Return %": round(opt_coc, 2)
        },
        "assumptions": [
            "If ADR increases by 10%",
            "If Occupancy increases by 10%",
            "If we negotiate a 5% discount on purchase price",
            "If operating expenses remain stable"
        ]
    }
