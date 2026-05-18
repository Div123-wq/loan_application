import json
from flask import Blueprint, request, jsonify
from routes.upload import get_document_text
from services.github_ai_service import chat_json

simulator_bp = Blueprint('simulator', __name__)

SIM_SYSTEM = """You are LoanLens AI — a precise financial simulator. 
Calculate exact financial impacts based on loan terms and user scenarios.
Always return structured JSON with specific numbers."""


@simulator_bp.route('/api/simulate/whatif', methods=['POST'])
def what_if_simulator():
    """Feature 5: What Happens If… Simulator"""
    data = request.get_json()
    doc_id = data.get('doc_id')
    scenario = data.get('scenario', '')  # e.g. "What if I miss 2 EMIs?"

    if not scenario:
        return jsonify({"error": "Scenario is required"}), 400

    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass

    prompt = f"""A loan borrower is asking: "{scenario}"

Loan document context:
{doc_text[:3000] if doc_text else "No document — use typical Indian home loan defaults: ₹25L, 8.5%, 20 years, EMI ~₹21,700"}

Simulate the exact financial and practical impact of this scenario.

Return JSON:
{{
  "scenario": "{scenario}",
  "immediate_impact": {{
    "penalty_amount": "₹2,170 (10% of EMI)",
    "extra_interest": "₹1,500",
    "total_extra_cost": "₹3,670"
  }},
  "timeline_effects": [
    {{"month": 1, "event": "Late fee charged", "cost": "₹2,170", "severity": "medium"}},
    {{"month": 2, "event": "Second miss — bank notice sent", "cost": "₹4,340", "severity": "high"}},
    {{"month": 3, "event": "Credit score drop ~50 points", "cost": "₹0", "severity": "critical"}}
  ],
  "credit_score_impact": "-30 to -80 points",
  "total_extra_payment": "₹15,000 over loan tenure",
  "recovery_timeline": "6-12 months to normalize",
  "bank_action_risk": "Low / Medium / High / Very High",
  "advice": [
    "Contact bank before missing payment",
    "Request EMI holiday if financial hardship",
    "Maintain 3-month emergency fund"
  ],
  "severity_level": "Medium",
  "plain_summary": "2-3 sentence friendly explanation of what would happen"
}}"""

    result = chat_json(SIM_SYSTEM, prompt)
    return jsonify({"success": True, **json.loads(result)})


@simulator_bp.route('/api/simulate/pressure', methods=['POST'])
def financial_pressure():
    """Feature 8: Emotional Financial Pressure Detector"""
    data = request.get_json()
    doc_id = data.get('doc_id')
    salary = data.get('salary', 0)
    expenses = data.get('expenses', 0)
    family_size = data.get('family_size', 2)
    obligations = data.get('obligations', '')  # school fees, rent, etc.

    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass

    prompt = f"""Analyze financial pressure for a loan borrower.

BORROWER PROFILE:
- Monthly Salary: ₹{salary:,}
- Monthly Expenses: ₹{expenses:,}
- Family Size: {family_size} members
- Other Obligations: {obligations}

LOAN DOCUMENT:
{doc_text[:2000] if doc_text else "Assume typical home loan: EMI ₹21,700/month"}

Calculate financial stress and predict pressure points.

Return JSON:
{{
  "monthly_surplus": 15000,
  "emi_to_income_ratio": 35.5,
  "stress_level": "Medium",
  "stress_score": 62,
  "monthly_calendar": [
    {{"month": "January", "stress": "Low", "note": "Normal month"}},
    {{"month": "February", "stress": "Low", "note": "Normal month"}},
    {{"month": "March", "stress": "High", "note": "Tax payments due"}},
    {{"month": "April", "stress": "Medium", "note": "School admissions"}},
    {{"month": "May", "stress": "Medium", "note": "Summer expenses"}},
    {{"month": "June", "stress": "High", "note": "School fees season"}},
    {{"month": "July", "stress": "Medium", "note": "Normal month"}},
    {{"month": "August", "stress": "Low", "note": "Normal month"}},
    {{"month": "September", "stress": "Medium", "note": "Festival preparations"}},
    {{"month": "October", "stress": "High", "note": "Diwali expenses likely"}},
    {{"month": "November", "stress": "Medium", "note": "Post-festival recovery"}},
    {{"month": "December", "stress": "High", "note": "Year-end expenses"}}
  ],
  "danger_months": ["March", "June", "October", "December"],
  "safe_months": ["January", "February", "August"],
  "lifestyle_impact": "You may need to cut discretionary spending by 20%",
  "breaking_point_months": 8,
  "breaking_point_note": "After 8 months, savings buffer may run out",
  "recommendations": [
    "Build emergency fund of 3x EMI before taking loan",
    "Avoid big purchases in March and October"
  ],
  "verdict": "2-3 sentence honest assessment"
}}"""

    result = chat_json(SIM_SYSTEM, prompt)
    return jsonify({"success": True, **json.loads(result)})


@simulator_bp.route('/api/simulate/deadline', methods=['POST'])
def deadline_predictor():
    """Feature 11: Deadline Panic Predictor"""
    data = request.get_json()
    doc_id = data.get('doc_id')
    start_date = data.get('start_date', '2024-01-01')
    salary = data.get('salary', 50000)

    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass

    prompt = f"""Predict upcoming financial deadlines and panic points for a loan borrower.

LOAN START DATE: {start_date}
MONTHLY SALARY: ₹{salary:,}
LOAN DOCUMENT: {doc_text[:2000] if doc_text else "Assume 20-year home loan, EMI ₹21,700/month"}

Predict upcoming financial stress periods overlaid with common Indian life events.

Return JSON:
{{
  "upcoming_milestones": [
    {{
      "date": "2024-03-31",
      "event": "First year completion",
      "type": "milestone",
      "financial_note": "₹2.2L paid, ₹22.8L remaining"
    }}
  ],
  "panic_periods": [
    {{
      "period": "June 2024",
      "reason": "School admission fees coincide with EMI",
      "risk_level": "High",
      "estimated_shortfall": "₹15,000",
      "advice": "Save ₹5,000 extra per month from March"
    }}
  ],
  "5_year_forecast": {{
    "easy_years": [1, 2],
    "challenging_years": [3, 5],
    "reason": "Salary growth typically outpaces EMI after year 3"
  }},
  "smart_tip": "Key actionable advice for the borrower"
}}"""

    result = chat_json(SIM_SYSTEM, prompt)
    return jsonify({"success": True, **json.loads(result)})
