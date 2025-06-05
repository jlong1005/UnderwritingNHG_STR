from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests
import numpy as np

app = FastAPI()

# Root route for health check
@app.get("/")
def read_root():
    return {"message": "NHG STR Underwriting API is live!"}


# Data model for optimization input
class OptimizationInput(BaseModel):
    zillow_url: str
    adr: float
    occupancy: float
    roi: float
    property_price: float
    tax_rate: float


@app.post("/optimize")
def optimize(input: OptimizationInput):
    # Extract values
    adr = input.adr
    occupancy = input.occupancy
    roi = input.roi
    property_price = input.property_price
    tax_rate = input.tax_rate

    # --- Original Calculations ---
    gross_income = adr * (occupancy / 100) * 365
    monthly_PI = (property_price * 0.8 * 0.07) / 12  # 7% loan on 80%
    annual_tax = property_price * (tax_rate / 100)
    NOI = gross_income - annual_tax
    cap_rate = (NOI / property_price) * 100
    cash_flow = gross_income - annual_tax - (monthly_PI * 12)
    coc_return = (cash_flow / (property_price * 0.2)) * 100  # 20% down

    original = {
        "Gross Annual Income": round(gross_income, 2),
        "Monthly P&I": round(monthly_PI, 2),
        "NOI": round(NOI, 2),
        "Cap Rate": round(cap_rate, 2),
        "Cash Flow (Monthly)": round(cash_flow / 12, 2),
        "Cash-on-Cash Return": round(coc_return, 2)
    }

    # --- Optimizations ---
    optimized = {
        "Gross Annual Income": round(gross_income * 1.1, 2),
        "Monthly P&I": round(monthly_PI, 2),
        "NOI": round(NOI * 1.1, 2),
        "Cap Rate": round((NOI * 1.1 / property_price) * 100, 2),
        "Cash Flow (Monthly)": round((cash_flow + (gross_income * 0.1)) / 12, 2),
        "Cash-on-Cash Return": round(((cash_flow + (gross_income * 0.1)) / (property_price * 0.2)) * 100, 2)
    }

    # --- Assumption Notes ---
    assumptions = [
        "If we increase ADR by 10%",
        "If occupancy improves by 10%",
        "If we can achieve our target ROI of {}%".format(roi),
        "If we negotiate 5% off the property price"
    ]

    return {
        "original_proforma": original,
        "optimized_proforma": optimized,
        "assumptions": assumptions
    }
