from fastapi import FastAPI
from pydantic import BaseModel
from lead_engine import lead_engine

app = FastAPI(title="Funding Qualification Engine")

class Lead(BaseModel):
    name: str
    country: str
    role: str
    business_type: str
    monthly_revenue: int
    credit_score: int
    time_in_business: int
    has_business_bank: bool
    funding_amount: int
    urgency: str
    needs_funding_days: int
    previous_funding: bool

@app.post("/qualify")
def qualify_lead(lead: Lead):
    result = lead_engine.invoke(lead.dict())
    return result
