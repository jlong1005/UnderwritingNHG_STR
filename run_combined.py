
import re
import requests
import numpy as np
import traceback
from str_underwriter import STRUnderwriter

def extract_zpid(zillow_url):
    match = re.search(r'/([0-9]+)_zpid', zillow_url)
    return match.group(1) if match else None

def fetch_property_data(zpid, api_key):
    url = "https://zillow-com1.p.rapidapi.com/property"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    querystring = {"zpid": zpid}
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def run_underwriter(inputs):
    model = STRUnderwriter(inputs)
    return model.get_results()

def optimize_model(base_inputs):
    adr = base_inputs["nightly_rate"]
    occupancy = base_inputs["occupancy_rate"]
    expense = base_inputs["expense_ratio"]
    price = base_inputs["purchase_price"]

    adr_range = np.linspace(adr * 0.9, adr * 1.1, 5)
    occupancy_range = np.linspace(occupancy * 0.9, occupancy * 1.1, 5)
    expense_range = np.linspace(0.25, 0.45, 5)
    price_options = [price, price * 0.95]

    best_result = None
    best_cashflow = -float("inf")

    for p in price_options:
        for a in adr_range:
            for o in occupancy_range:
                for e in expense_range:
                    trial_inputs = base_inputs.copy()
                    trial_inputs.update({
                        "purchase_price": p,
                        "nightly_rate": a,
                        "occupancy_rate": o,
                        "expense_ratio": e
                    })
                    results = run_underwriter(trial_inputs)
                    cash_flow = results.get("Cash Flow (Monthly)", -999999)
                    if cash_flow > best_cashflow:
                        best_cashflow = cash_flow
                        best_result = results.copy()
                        best_result.update({
                            "ADR": round(a, 2),
                            "Occupancy Rate": round(o * 100, 1),
                            "Expense Ratio": round(e * 100, 1),
                            "Purchase Price": round(p, 2)
                        })

    return best_result

if __name__ == "__main__":
    try:
        url = input("Paste a Zillow URL: ").strip()
        zpid = extract_zpid(url)
        if not zpid:
            print("❌ Could not extract ZPID from URL.")
        else:
            print(f"Extracted ZPID: {zpid}")
            api_key = input("Enter your RapidAPI Key: ").strip()
            zillow_data = fetch_property_data(zpid, api_key)
            print("\n✅ Zillow Data Retrieved")
            for key in ["address", "price", "bedrooms", "bathrooms", "livingArea", "propertyTaxRate", "hoaFee"]:
                print(f"{key}: {zillow_data.get(key, 'N/A')}")

            nightly_rate = float(input("\nEnter Average Daily Rate (ADR): $"))
            occupancy_input = float(input("Enter Occupancy Rate (percent): "))
            occupancy_rate = occupancy_input / 100.0

            price = float(zillow_data.get("price", 0))
            taxes = float(zillow_data.get("taxAssessedValue", 6000)) * 0.015

            base_inputs = {
                "purchase_price": price,
                "loan_pct": 0.75,
                "interest_rate": 0.07,
                "term_years": 30,
                "occupancy_rate": occupancy_rate,
                "nightly_rate": nightly_rate,
                "expense_ratio": 0.3,
                "property_tax": taxes,
                "insurance": 1800
            }

            original = run_underwriter(base_inputs)
            optimized = optimize_model(base_inputs)

            print("\n📊 Original Proforma:")
            for k, v in original.items():
                print(f"{k}: ${v}")

            print("\n🚀 Optimized Proforma:")
            for k, v in optimized.items():
                print(f"{k}: ${v}")

            print("\n🧩 Optimization Used These Assumptions:")
            print(f"- If we {'achieve a 5% discount' if optimized['Purchase Price'] < base_inputs['purchase_price'] else 'use the listed price'} on the purchase price")
            print(f"- If we set ADR to ${optimized['ADR']}")
            print(f"- If occupancy rate is {optimized['Occupancy Rate']}%")
            print(f"- If expense ratio is {optimized['Expense Ratio']}%")

    except Exception as e:
        print("\n❌ An unexpected error occurred:")
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
