from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

# =========================
# Lead State
# =========================

class LeadState(TypedDict):
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
    intent_score: int
    qualified: bool
    rejection_reason: Optional[str]

# =========================
# ICP ENFORCEMENT
# =========================

def icp_gate(state: LeadState):
    if state["country"] not in ["US", "Canada"]:
        return {**state, "qualified": False, "rejection_reason": "Non US/Canada"}

    if state["role"].lower() not in ["owner","founder","co-founder","managing partner","ceo","president"]:
        return {**state, "qualified": False, "rejection_reason": "Not decision maker"}

    if not state["has_business_bank"]:
        return {**state, "qualified": False, "rejection_reason": "No business bank"}

    if state["business_type"] != "for-profit":
        return {**state, "qualified": False, "rejection_reason": "Non-profit"}

    return {**state, "qualified": True}

# =========================
# FINANCIAL QUALIFICATION
# =========================

def financial_gate(state: LeadState):
    if state["country"] == "US":
        if state["credit_score"] < 575 or state["monthly_revenue"] < 30000 or state["time_in_business"] < 12:
            return {**state, "qualified": False, "rejection_reason": "Failed US Financial Thresholds"}
    else:
        if state["credit_score"] < 500 or state["monthly_revenue"] < 10000 or state["time_in_business"] < 6:
            return {**state, "qualified": False, "rejection_reason": "Failed Canada Financial Thresholds"}

    return {**state, "qualified": True}

# =========================
# INTENT SCORING
# =========================

def intent_scoring(state: LeadState):
    score = 0
    if state["needs_funding_days"] <= 30:
        score += 25
    if state["urgency"] == "high":
        score += 30
    if state["previous_funding"]:
        score += 10
    if state["funding_amount"] >= 50000:
        score += 10

    return {**state, "intent_score": score, "qualified": score >= 70}

# =========================
# LIVE TRANSFER READINESS
# =========================

def live_transfer_gate(state: LeadState):
    if not state["qualified"]:
        return {**state, "qualified": False, "rejection_reason": "Intent score too low"}
    return {**state, "qualified": True}

# =========================
# GRAPH
# =========================

graph = StateGraph(LeadState)

graph.add_node("ICP", icp_gate)
graph.add_node("FINANCIAL", financial_gate)
graph.add_node("INTENT", intent_scoring)
graph.add_node("LIVE", live_transfer_gate)

graph.set_entry_point("ICP")

graph.add_conditional_edges("ICP", lambda s: "FINANCIAL" if s["qualified"] else END)
graph.add_conditional_edges("FINANCIAL", lambda s: "INTENT" if s["qualified"] else END)
graph.add_conditional_edges("INTENT", lambda s: "LIVE" if s["qualified"] else END)
graph.add_edge("LIVE", END)

lead_engine = graph.compile()
