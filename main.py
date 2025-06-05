from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UnderwriteRequest(BaseModel):
    url: str
    adr: float
    occupancy: float
    roi_target: float

@app.post("/api/underwrite")
def underwrite(data: UnderwriteRequest):
    # Here you can replace this with your actual underwriting logic
    optimized_data = {
        "original_inputs": {
            "Zillow URL": data.url,
            "ADR": data.adr,
            "Occupancy": data.occupancy,
            "Target ROI": data.roi_target,
        },
        "recommendation": {
            "message": "Example optimization logic here",
            "suggested_price_reduction": "5%",
            "adjusted_roi": round(data.adr * data.occupancy / 100 / 365 / 2, 2)  # just dummy logic
        },
        "assumptions": [
            "If we achieve a 5% discount on purchase price",
            "If ADR is accurate within ±10%",
            "If occupancy remains stable",
        ]
    }
    return optimized_data
