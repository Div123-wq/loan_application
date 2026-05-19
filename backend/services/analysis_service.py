import json
from services.github_ai_service import chat_json, chat

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────

ANALYZER_SYSTEM = """You are LoanLens AI — an expert financial intelligence analyst specializing in multi-category consumer agreements.
You analyze loan contracts, health/life/general insurance policies, pet adoption & care agreements, residential leases, and financial papers with deep expertise in:
- Hidden clauses, penalty structures, and unilateral adjustment triggers
- Multi-industry regulations (banking, insurance clauses, pet welfare, and leasing laws)
- Risk assessment, coverage exclusions, and financial impact analysis
- Plain-language explanation of legal/financial jargon

Always be precise, helpful, and highly protective of the consumer's/borrower's interests.
Return structured JSON responses as instructed."""


# ─────────────────────────────────────────────
# UNIFIED HIGH-FIDELITY MASTER ANALYSIS ENGINE
# ─────────────────────────────────────────────

def perform_master_analysis(document_text: str) -> dict:
    """Runs a single comprehensive, high-fidelity prompt extracting all 12 analytical fields simultaneously.
    
    This avoids context isolation, parses up to 100,000 characters of the document text fully,
    and returns perfectly synchronized financial metrics, risk scores, and hidden trap detections.
    """
    # Clean and slice text to keep it safely within premium token limits
    safe_text = document_text[:100000]
    
    prompt = f"""You are LoanLens AI — the premium financial intelligence analyst.
Analyze the provided document text (which may be a loan agreement, insurance policy, lease, or pet agreement) in its entirety to generate a high-fidelity, synchronized audit.
Identify all core parameters, hidden trap clauses, risk assessments, jargon explanations, suspicious markers, and trust metrics.

DOCUMENT TEXT:
{safe_text}

You must return a single JSON object containing exactly this structure, with no extra text or explanations. Ensure all numeric amounts are parsed as numbers:

{{
  "core_info": {{
    "loan_type": "string (e.g. Home Loan, Personal Loan, Health Insurance, Pet Agreement, Lease)",
    "lender_name": "string (name of the financial institution or other party)",
    "borrower_name": "string (full name of borrower/consumer/tenant)",
    "loan_amount": "string (formatted amount/coverage amount/rent, e.g. ₹50,00,000 or ₹12,000/mo)",
    "loan_amount_numeric": 5000000,
    "interest_rate": "string (interest rate, deductible rate, or monthly increase rate, e.g. 8.5% p.a. or N/A)",
    "interest_rate_numeric": 8.5,
    "interest_type": "Fixed / Floating / Mixed / Not specified / Not applicable",
    "tenure": "string (e.g. 20 years or 11 months)",
    "tenure_months": 240,
    "emi_amount": "string (estimated monthly EMI or rent premium, e.g. ₹43,391 or ₹1,200)",
    "emi_numeric": 43391,
    "processing_fee": "string (processing charges or deposit fee, e.g. ₹10,000)",
    "document_date": "string (e.g. 18 May 2026)",
    "summary": "Provide a comprehensive, high-value summary of the document (4-6 detailed sentences or bullet points). For loans, focus on rates and foreclosure penalties. For insurance, pet policies, or leases, provide a highly detailed and thorough overview covering co-payment ratios, room rent sub-limits, waiting periods, and major disease/claim exclusions, highlighting the most critical consumer warnings.",
    "document_quality": "Clear / Partially Clear / Unclear"
  }},
  "hidden_traps": [
    {{
      "id": 1,
      "title": "Short descriptive title of the trap (e.g., Unilateral Floating Margin Clause)",
      "severity": "Critical / High / Medium / Low",
      "original_text": "EXACT VERBATIM QUOTE (case-sensitive, with exact spaces, symbols, and text) of the offending sentence/phrase as it appears in the DOCUMENT TEXT. This is critical for exact highlighting in the PDF.",
      "plain_explanation": "What this means in simple, everyday language",
      "impact": "Concrete financial penalty, coverage exclusion, or risk the consumer faces",
      "advice": "Actionable advice or specific negotiation question the consumer can ask"
    }}
  ],
  "friendly_explanations": [
    {{
      "legal_text": "Confusing legalese/formal clause from the contract",
      "friendly_text": "What a trusted friend would explain this means to you",
      "emoji": "emoji (e.g., 💸, 📈, ⚖️)",
      "category": "Interest / Penalty / Rights / Insurance / Repayment"
    }}
  ],
  "risk_score": {{
    "overall_score": 60,
    "overall_level": "Medium Risk",
    "overall_color": "amber",
    "sub_scores": {{
      "penalty_risk": 80,
      "interest_stability": 40,
      "transparency": 75,
      "fairness": 70,
      "legal_complexity": 50
    }},
    "verdict": "Comprehensive 2-sentence summary explaining the calculated risk profile.",
    "top_risk_factor": "The single most dangerous threat clause identified"
  }},
  "suspicious_clauses": {{
    "overall_suspicion": "Clean / Minor Concerns / Suspicious / Highly Suspicious",
    "suspicious_items": [
      {{
        "id": 1,
        "flag": "High Administrative Charge / Vague Legal Indemnity etc.",
        "confidence": 85,
        "reason": "Why this specific clause raises flags against typical consumer loans",
        "original_text": "The flagged text block",
        "industry_standard": "What is normal or standard industry practice",
        "severity": "Fraud Risk / High Concern / Unusual / Mild Concern"
      }}
    ]
  }},
  "trust_score": {{
    "transparency_score": 75,
    "transparency_note": "Detail on score reasoning",
    "fairness_score": 60,
    "fairness_note": "Detail on score reasoning",
    "complexity_score": 45,
    "complexity_note": "Detail on score reasoning",
    "trust_grade": "B",
    "trust_grade_label": "Fairly Trustworthy",
    "trust_summary": "Expert summary of document trustworthiness, readability, and structural bias."
  }}
}}

Ensure you find between 3 to 6 high-fidelity hidden traps, 4 to 6 jargon explanations, and 2 to 4 suspicious indicators. If the document text lacks details, extrapolate standard guidelines for this loan type to guarantee full value.
Respond ONLY with a single valid JSON block."""

    result = chat_json(ANALYZER_SYSTEM, prompt)
    return json.loads(result)


# ─────────────────────────────────────────────
# BACKWARDS COMPATIBILITY HELPERS
# ─────────────────────────────────────────────

def analyze_document_core(document_text: str) -> dict:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("core_info", {})

def detect_hidden_traps(document_text: str) -> list:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("hidden_traps", [])

def explain_like_friend(document_text: str) -> list:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("friendly_explanations", [])

def calculate_risk_score(document_text: str, traps: list = None) -> dict:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("risk_score", {})

def detect_suspicious_clauses(document_text: str) -> list:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("suspicious_clauses", {})

def calculate_trust_score(document_text: str) -> dict:
    """For legacy routing compatibility."""
    return perform_master_analysis(document_text).get("trust_score", {})


# ─────────────────────────────────────────────
# FEATURE 4: Reality Cost Calculator (Local CPU Math)
# ─────────────────────────────────────────────

def calculate_reality_cost(core_info: dict) -> dict:
    """Calculate the true total cost of the loan with local precision arithmetic."""
    loan_type = str(core_info.get("loan_type", "")).lower()
    principal = core_info.get("loan_amount_numeric") or 500000
    rate = core_info.get("interest_rate_numeric") or 12.0
    months = core_info.get("tenure_months") or 60
    emi = core_info.get("emi_numeric") or 0

    # Ensure valid numbers
    try:
        principal = float(principal)
        rate = float(rate)
        months = int(months)
        emi = float(emi)
    except:
        principal = 500000
        rate = 12.0
        months = 60
        emi = 0

    is_insurance = "insurance" in loan_type or "policy" in loan_type or "pet" in loan_type or "animal" in loan_type
    is_lease = "lease" in loan_type or "rent" in loan_type

    if is_insurance:
        total_payment = emi * months
        # For insurance, UI maps total_interest to "Co-pay Exposure". Estimate at 20% of Sum Insured.
        total_interest = principal * 0.20
        interest_percentage = 20.0
        shock_statement = f"You will pay ₹{total_payment:,.0f} in premiums over {months} months, with an estimated ₹{total_interest:,.0f} out-of-pocket co-pay exposure."
        
        yearly_breakdown = []
        for year in range(1, (months // 12) + 2):
            if (year - 1) * 12 >= months:
                break
            yearly_breakdown.append({
                "year": year,
                "emi_paid": round(emi * 12, 0),
                "interest_paid": 0,
                "principal_paid": 0,
                "remaining_balance": round(principal, 0)
            })

        return {
            "principal": round(principal, 0),
            "emi_amount": round(emi, 0),
            "total_payment": round(total_payment, 0),
            "total_interest": round(total_interest, 0),
            "interest_percentage": interest_percentage,
            "yearly_breakdown": yearly_breakdown,
            "shock_statement": shock_statement
        }

    elif is_lease:
        total_payment = emi * months
        # For lease, UI maps total_interest to Deposit exposure.
        total_interest = principal  
        interest_percentage = 0.0
        shock_statement = f"You will pay ₹{total_payment:,.0f} in total rent over {months} months, with ₹{principal:,.0f} locked as security deposit."

        yearly_breakdown = []
        for year in range(1, (months // 12) + 2):
            if (year - 1) * 12 >= months:
                break
            yearly_breakdown.append({
                "year": year,
                "emi_paid": round(emi * 12, 0),
                "interest_paid": 0,
                "principal_paid": 0,
                "remaining_balance": 0
            })

        return {
            "principal": round(principal, 0),
            "emi_amount": round(emi, 0),
            "total_payment": round(total_payment, 0),
            "total_interest": round(total_interest, 0),
            "interest_percentage": interest_percentage,
            "yearly_breakdown": yearly_breakdown,
            "shock_statement": shock_statement
        }

    # DEFAULT LOAN LOGIC
    if emi == 0 and rate > 0:
        monthly_rate = rate / 12 / 100
        if monthly_rate > 0:
            emi = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)

    total_payment = emi * months
    total_interest = total_payment - principal

    # Build year-by-year breakdown
    yearly_breakdown = []
    remaining = principal
    monthly_rate = rate / 12 / 100
    
    total_months = months
    for year in range(1, min(int(total_months / 12) + 2, 31)):
        year_interest = 0
        year_principal = 0
        for _ in range(min(12, total_months)):
            interest_part = remaining * monthly_rate
            principal_part = emi - interest_part
            year_interest += interest_part
            year_principal += principal_part
            remaining -= principal_part
            total_months -= 1
            if total_months <= 0:
                break
        yearly_breakdown.append({
            "year": year,
            "emi_paid": round(emi * 12, 0),
            "interest_paid": round(year_interest, 0),
            "principal_paid": round(year_principal, 0),
            "remaining_balance": round(max(remaining, 0), 0)
        })
        if total_months <= 0:
            break

    return {
        "principal": round(principal, 0),
        "emi_amount": round(emi, 0),
        "total_payment": round(total_payment, 0),
        "total_interest": round(total_interest, 0),
        "interest_percentage": round((total_interest / principal * 100) if principal > 0 else 0, 1),
        "yearly_breakdown": yearly_breakdown,
        "shock_statement": f"You will pay ₹{total_interest:,.0f} extra as interest — {round(total_interest/principal*100 if principal>0 else 0, 1)}% more than you borrowed!"
    }

