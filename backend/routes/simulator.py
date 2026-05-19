import json
import re
from flask import Blueprint, request, jsonify
from routes.upload import get_document_text
from services.github_ai_service import chat_json

simulator_bp = Blueprint('simulator', __name__)

SIM_SYSTEM = """You are FinScan AI — a precise financial contract simulator. 
Calculate exact financial impacts based on loan, lease, or insurance terms and user scenarios.
Always return structured JSON with category-appropriate numbers and friendly explanations."""


def detect_category(doc_text: str, scenario: str) -> str:
    """Robust Category Detection Scoring Engine for the Simulator."""
    doc_lower = doc_text.lower() if doc_text else ""
    
    # Calculate score weight for each document category
    pet_score = 0
    pet_words = [r"\bpet\b", r"\bdog\b", r"\bcat\b", r"\bveterinary\b", r"\banimal\b", r"\badoption\b", r"\bbreed\b"]
    for pat in pet_words:
        pet_score += len(re.findall(pat, doc_lower)) * 5

    ins_score = 0
    ins_words = [r"\binsurance policy\b", r"\bhealth insurance\b", r"\blife insurance\b", r"\bsum insured\b", r"\bco-payment\b", r"\bco-pay\b", r"\binsurer\b", r"\bclaim proceeds\b", r"\bwaiting period\b"]
    for pat in ins_words:
        ins_score += len(re.findall(pat, doc_lower)) * 5
    for pat in [r"\binsurance\b", r"\bpolicy\b", r"\bpremium\b", r"\bdeductible\b"]:
        ins_score += len(re.findall(pat, doc_lower)) * 1

    lease_score = 0
    lease_words = [r"\blease\b", r"\btenant\b", r"\blandlord\b", r"\brent\b", r"\bsecurity deposit\b", r"\bpremises\b", r"\blessor\b", r"\blessee\b", r"\btenancy\b"]
    for pat in lease_words:
        lease_score += len(re.findall(pat, doc_lower)) * 5

    loan_score = 0
    loan_words = [r"\bloan agreement\b", r"\bloan amount\b", r"\bprincipal amount\b", r"\bborrower\b", r"\blender\b", r"\brepayment\b", r"\bemi\b", r"\bequated monthly\b", r"\binterest rate\b", r"\bmclr\b", r"\bmortgage\b", r"\bforeclosure\b", r"\bprepayment\b"]
    for pat in loan_words:
        loan_score += len(re.findall(pat, doc_lower)) * 5

    category = "Loan"
    scores = {"Pet": pet_score, "Insurance": ins_score, "Lease": lease_score, "Loan": loan_score}
    max_cat = max(scores, key=scores.get)
    if scores[max_cat] > 0:
        category = max_cat
    else:
        # Fallback category based on scenario text
        scen_lower = scenario.lower() if scenario else ""
        if any(w in scen_lower for w in ["pet", "dog", "cat", "vet", "breed"]):
            category = "Pet"
        elif any(w in scen_lower for w in ["policy", "insurance", "insurer", "premium", "co-pay", "claim"]):
            category = "Insurance"
        elif any(w in scen_lower for w in ["rent", "lease", "landlord", "tenant", "deposit"]):
            category = "Lease"
        else:
            category = "Loan"
            
    return category


@simulator_bp.route('/api/simulate/whatif', methods=['POST'])
def what_if_simulator():
    """Feature 5: What Happens If… Simulator"""
    data = request.get_json() or {}
    doc_id = data.get('doc_id')
    scenario = data.get('scenario', '')  # e.g. "What if I miss 2 EMIs?"
    commitment = float(data.get('commitment') or 0)
 
    if not scenario:
        return jsonify({"error": "Scenario is required"}), 400
 
    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass
 
    category = detect_category(doc_text, scenario)
    
    if not commitment:
        if category == "Pet":
            commitment = 1250
        elif category == "Insurance":
            commitment = 708
        elif category == "Lease":
            commitment = 22000
        else:
            commitment = 21700

    # Precise mathematical calculations for late misses or standard scenarios
    late_fee = int(0.10 * commitment if category in ["Loan", "Lease"] else 0.20 * commitment)
    extra_interest = int(0.05 * commitment if category == "Loan" else 0)
    total_extra_cost = (late_fee * 2) + extra_interest

    if category == "Pet":
        defaults = f"typical Indian pet policy defaults: Sum Insured ₹10L, Premium ₹{commitment:,.0f}/month, Co-pay 20%"
        actor = "pet owner"
        doc_label = "pet policy"
        penalty_placeholder = f"₹{late_fee:,} (20% co-payment exposure deviation)"
    elif category == "Insurance":
        defaults = f"typical Indian health insurance defaults: Sum Insured ₹5L, Premium ₹{commitment:,.0f}/month, Co-pay 20%"
        actor = "policyholder"
        doc_label = "insurance policy"
        penalty_placeholder = f"₹{late_fee:,} (20% surgery co-pay penalty)"
    elif category == "Lease":
        defaults = f"typical residential lease defaults: Monthly Rent ₹{commitment:,.0f}, Security Deposit ₹{commitment*2:,.0f}, 11-month tenure"
        actor = "tenant"
        doc_label = "lease agreement"
        penalty_placeholder = f"₹{late_fee:,} (10% late rent penalty)"
    else:
        defaults = f"typical Indian home loan defaults: ₹25L, 8.5%, 20 years, EMI ~₹{commitment:,.0f}"
        actor = "loan borrower"
        doc_label = "loan document"
        penalty_placeholder = f"₹{late_fee:,} (10% of EMI late payment penalty)"
 
    prompt = f"""A {actor} is asking: "{scenario}"
 
 {doc_label.capitalize()} context:
 {doc_text[:3000] if doc_text else f"No document — use {defaults}"}
 
 SCENARIO MATHEMATICAL VALUES:
 - Monthly Commitment amount: ₹{commitment:,}
 - Late Fee Per Occurrence: ₹{late_fee:,}
 - Extra Interest Charge: ₹{extra_interest:,}
 - Estimated Total Extra Outlay: ₹{total_extra_cost:,}
 
 Simulate the exact financial and practical impact of this scenario for a {category} document.
 You must use the pre-calculated SCENARIO MATHEMATICAL VALUES in your response JSON fields exactly.
 
 Return JSON:
 {{
   "scenario": "{scenario}",
   "immediate_impact": {{
     "penalty_amount": "{penalty_placeholder}",
     "extra_interest": "₹{extra_interest:,}",
     "total_extra_cost": "₹{total_extra_cost:,}"
   }},
   "timeline_effects": [
     {{"month": 1, "event": "Late fee charged / premium shock applied", "cost": "₹{late_fee:,}", "severity": "medium"}},
     {{"month": 2, "event": "Second miss / contract notice dispatched", "cost": "₹{late_fee * 2:,}", "severity": "high"}},
     {{"month": 3, "event": "Credit rating impact / exclusion window triggers", "cost": "₹0", "severity": "critical"}}
   ],
   "credit_score_impact": "-30 to -80 points (or policy voidability risks)",
   "total_extra_payment": "₹{total_extra_cost:,} over tenure",
   "recovery_timeline": "6-12 months to normalize",
   "bank_action_risk": "Low / Medium / High / Very High",
   "advice": [
     "Contact counterparty prior to missing timeline",
     "Audit contract exclusions thoroughly"
   ],
   "severity_level": "Medium",
   "plain_summary": "2-3 sentence friendly explanation of what would happen matching this category"
 }}"""
 
    result = chat_json(SIM_SYSTEM, prompt)
    res_dict = json.loads(result)
    
    # Overwrite with guaranteed math values
    if "immediate_impact" not in res_dict:
        res_dict["immediate_impact"] = {}
    res_dict["immediate_impact"]["penalty_amount"] = penalty_placeholder
    res_dict["immediate_impact"]["extra_interest"] = f"₹{extra_interest:,}"
    res_dict["immediate_impact"]["total_extra_cost"] = f"₹{total_extra_cost:,}"
    res_dict["total_extra_payment"] = f"₹{total_extra_cost:,}"
    
    return jsonify({"success": True, **res_dict})


@simulator_bp.route('/api/simulate/pressure', methods=['POST'])
def financial_pressure():
    """Feature 8: Emotional Financial Pressure Detector"""
    data = request.get_json() or {}
    doc_id = data.get('doc_id')
    salary = float(data.get('salary') or 0)
    expenses = float(data.get('expenses') or 0)
    family_size = int(data.get('family_size') or 2)
    obligations = data.get('obligations', '')  # school fees, rent, etc.
    commitment = float(data.get('commitment') or 0)
 
    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass
 
    category = detect_category(doc_text, "")
    
    if not commitment:
        if category == "Pet":
            commitment = 1250
        elif category == "Insurance":
            commitment = 708
        elif category == "Lease":
            commitment = 22000
        else:
            commitment = 21700

    # Robust local mathematical calculations
    monthly_surplus = salary - expenses - commitment
    ratio = (commitment / salary * 100) if salary > 0 else 0
    
    # Calculate stress score and level mathematically
    if salary <= 0:
        stress_score = 100
        stress_level = "Critical"
    else:
        disposable = salary - expenses
        if disposable <= 0:
            stress_score = 95
            stress_level = "Critical"
        else:
            stress_score = int(min(100, max(0, (commitment / disposable) * 100)))
            
        if stress_score > 75:
            stress_level = "Critical"
        elif stress_score > 50:
            stress_level = "High"
        elif stress_score > 30:
            stress_level = "Medium"
        else:
            stress_level = "Low"
 
    if category == "Pet":
        defaults = f"typical pet policy: Premium ₹{commitment:,.0f}/month"
        actor = "pet owner"
        doc_label = "pet policy"
    elif category == "Insurance":
        defaults = f"typical health insurance: Premium ₹{commitment:,.0f}/month"
        actor = "policyholder"
        doc_label = "insurance policy"
    elif category == "Lease":
        defaults = f"typical lease: Monthly Rent ₹{commitment:,.0f}"
        actor = "tenant"
        doc_label = "lease agreement"
    else:
        defaults = f"typical home loan: EMI ₹{commitment:,.0f}/month"
        actor = "loan borrower"
        doc_label = "loan document"
 
    prompt = f"""Analyze financial pressure and budget elasticity for a {actor}.
 
 BORROWER PROFILE:
 - Monthly Salary: ₹{salary:,}
 - Monthly Expenses: ₹{expenses:,}
 - Family Size: {family_size} members
 - Other Obligations: {obligations}
 
 MATHEMATICALLY CALCULATED CONSTRAINTS (YOU MUST ENFORCE THESE EXACTLY):
 - Monthly Contract Commitment: ₹{commitment:,}
 - Calculated Monthly Cash Surplus (Salary - Expenses - Commitment): ₹{monthly_surplus:,}
 - Commitment-to-Income Ratio: {ratio:.1f}%
 - Mathematical Stress Score: {stress_score}%
 - Mathematical Stress Level: {stress_level}
 
 {doc_label.upper()} DETAILS:
 {doc_text[:2000] if doc_text else f"Assume {defaults}"}
 
 Calculate financial stress and predict pressure points.
 Enforce the mathematically calculated values into the JSON response fields exactly.
 
 Return JSON:
 {{
   "monthly_surplus": {monthly_surplus},
   "emi_to_income_ratio": {ratio:.1f},
   "stress_level": "{stress_level}",
   "stress_score": {stress_score},
   "monthly_calendar": [
     {{"month": "January", "stress": "Low", "note": "Normal baseline month"}},
     {{"month": "February", "stress": "Low", "note": "Normal baseline month"}},
     {{"month": "March", "stress": "High", "note": "Tax outlays and financial closing"}},
     {{"month": "April", "stress": "Medium", "note": "Standard reserves"}},
     {{"month": "May", "stress": "Medium", "note": "Vacation outlays"}},
     {{"month": "June", "stress": "High", "note": "Academic school fees due"}},
     {{"month": "July", "stress": "Medium", "note": "Normal baseline month"}},
     {{"month": "August", "stress": "Low", "note": "Normal baseline month"}},
     {{"month": "September", "stress": "Medium", "note": "Festival preparation outlays"}},
     {{"month": "October", "stress": "High", "note": "Festive Diwali outlays"}},
     {{"month": "November", "stress": "Medium", "note": "Post-festival adjustments"}},
     {{"month": "December", "stress": "High", "note": "Year-end holiday outlays"}}
   ],
   "danger_months": ["March", "June", "October", "December"],
   "safe_months": ["January", "February", "August"],
   "lifestyle_impact": "You have a monthly surplus of ₹{monthly_surplus:,} which places you at a {stress_level} stress profile.",
   "breaking_point_months": {3 if stress_level in ["High", "Critical"] else 12},
   "breaking_point_note": "Based on a ₹{monthly_surplus:,} surplus, your safety buffer provides cover for about {3 if stress_level in ['High', 'Critical'] else 12} months.",
   "recommendations": [
     "Maintain a dedicated liquidity pool for high-spending months.",
     "Optimize expenses to absorb the ₹{commitment:,} commitment."
   ],
   "verdict": "Provide a tailored 2-sentence description referencing the commitment of ₹{commitment:,} and salary of ₹{salary:,}."
 }}"""
 
    result = chat_json(SIM_SYSTEM, prompt)
    res_dict = json.loads(result)
    
    # Overwrite mathematically calculated metrics deterministically
    res_dict["monthly_surplus"] = monthly_surplus
    res_dict["emi_to_income_ratio"] = round(ratio, 1)
    res_dict["stress_score"] = stress_score
    res_dict["stress_level"] = stress_level
    
    return jsonify({"success": True, **res_dict})


@simulator_bp.route('/api/simulate/deadline', methods=['POST'])
def deadline_predictor():
    """Feature 11: Deadline Panic Predictor"""
    data = request.get_json() or {}
    doc_id = data.get('doc_id')
    start_date = data.get('start_date', '2024-01-01')
    salary = float(data.get('salary') or 50000)
    commitment = float(data.get('commitment') or 0)
 
    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass
 
    category = detect_category(doc_text, "")
    
    if not commitment:
        if category == "Pet":
            commitment = 1250
        elif category == "Insurance":
            commitment = 708
        elif category == "Lease":
            commitment = 22000
        else:
            commitment = 21700
 
    if category == "Pet":
        defaults = f"typical 12-month pet policy, Premium ₹{commitment:,.0f}/month"
        actor = "pet owner"
        doc_label = "pet policy"
    elif category == "Insurance":
        defaults = f"typical annual health policy, Premium ₹{commitment:,.0f}/month"
        actor = "policyholder"
        doc_label = "insurance policy"
    elif category == "Lease":
        defaults = f"typical 11-month lease, Rent ₹{commitment:,.0f}/month"
        actor = "tenant"
        doc_label = "lease agreement"
    else:
        defaults = f"typical 20-year home loan, EMI ₹{commitment:,.0f}/month"
        actor = "loan borrower"
        doc_label = "loan document"
 
    prompt = f"""Predict upcoming financial deadlines and panic points for a {actor}.
 
 CONTRACT START DATE: {start_date}
 MONTHLY SALARY: ₹{salary:,}
 MONTHLY COMMITMENT: ₹{commitment:,}
 
 {doc_label.upper()} SPECIFICS: {doc_text[:2000] if doc_text else f"Assume {defaults}"}
 
 Predict upcoming financial stress periods overlaid with common Indian life events.
 
 Return JSON:
 {{
   "upcoming_milestones": [
     {{
       "date": "First Year Anniversary",
       "event": "Contract Term Anniversary Review",
       "type": "milestone",
       "financial_note": "A total cumulative contract premium/obligation of ₹{commitment * 12:,} paid."
     }}
   ],
   "panic_periods": [
     {{
       "period": "June Period",
       "reason": "Academic/school outlays coincide with commitment of ₹{commitment:,}",
       "risk_level": "High",
       "estimated_shortfall": "₹15,000",
       "advice": "Keep a buffer of at least 1x commitment (₹{commitment:,}) specifically for this season."
     }}
   ],
   "5_year_forecast": {{
     "easy_years": [1, 2],
     "challenging_years": [3, 5],
     "reason": "Standard indexation adjustments or renewal rate hikes kick in after Year 2."
   }},
   "smart_tip": "Actively track payment schedules and clear obligations before holidays to maintain rating status."
 }}"""
 
    result = chat_json(SIM_SYSTEM, prompt)
    res_dict = json.loads(result)
    
    # Overwrite milestones and panics mathematically
    if "upcoming_milestones" in res_dict and len(res_dict["upcoming_milestones"]) > 0:
        res_dict["upcoming_milestones"][0]["financial_note"] = f"A total cumulative contract premium/obligation of ₹{commitment * 12:,.0f} paid."
    if "panic_periods" in res_dict and len(res_dict["panic_periods"]) > 0:
        res_dict["panic_periods"][0]["advice"] = f"Keep a buffer of at least 1x commitment (₹{commitment:,.0f}) specifically for this season."
        res_dict["panic_periods"][0]["reason"] = f"Academic/school outlays coincide with monthly commitment of ₹{commitment:,.0f}."
        
    return jsonify({"success": True, **res_dict})

