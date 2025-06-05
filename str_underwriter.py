
import math

class STRUnderwriter:
    def __init__(self, inputs):
        self.inputs = inputs
        self.calculate_proforma()

    def calculate_proforma(self):
        price = self.inputs.get("purchase_price", 0)
        loan_pct = self.inputs.get("loan_pct", 0.75)
        loan_amount = price * loan_pct
        equity = price - loan_amount

        interest_rate = self.inputs.get("interest_rate", 0.07)
        term_years = self.inputs.get("term_years", 30)
        occupancy_rate = self.inputs.get("occupancy_rate", 0.65)
        nightly_rate = self.inputs.get("nightly_rate", 300)
        operating_expense_pct = self.inputs.get("expense_ratio", 0.3)
        property_tax = self.inputs.get("property_tax", 6000)
        insurance = self.inputs.get("insurance", 2000)

        r = interest_rate / 12
        n = term_years * 12
        monthly_pi = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

        gross_annual_income = nightly_rate * 365 * occupancy_rate
        gross_monthly_income = gross_annual_income / 12
        operating_expenses = gross_annual_income * operating_expense_pct
        noi = gross_annual_income - operating_expenses

        cash_flow = (gross_monthly_income - monthly_pi - (property_tax + insurance) / 12)
        coc_return = (cash_flow * 12) / equity if equity else 0
        cap_rate = noi / price if price else 0

        self.results = {
            "Gross Annual Income": round(gross_annual_income, 2),
            "Monthly P&I": round(monthly_pi, 2),
            "NOI": round(noi, 2),
            "Cap Rate": round(cap_rate * 100, 2),
            "Cash Flow (Monthly)": round(cash_flow, 2),
            "Cash-on-Cash Return": round(coc_return * 100, 2)
        }

    def get_results(self):
        return self.results
