from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ Enable CORS so frontend can contact backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UnderwriteRequest(BaseModel):
    url: str
    adr: float
    occupancy: float
    roi_target: float

@app.post("/api/underwrite")
def underwrite(data: UnderwriteRequest):
    # Example underwriting logic (replace later)
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
            "adjusted_roi": round(data.adr * data.occupancy / 100 / 365 / 2, 2)  # dummy math
        },
        "assumptions": [
            "If we achieve a 5% discount on purchase price",
            "If ADR is accurate within ±10%",
            "If occupancy remains stable",
        ]
    }
    return optimized_data
