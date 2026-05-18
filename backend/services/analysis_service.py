import json
from services.github_ai_service import chat_json, chat

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────

ANALYZER_SYSTEM = """You are LoanLens AI — an expert financial intelligence analyst specializing in loan documents.
You analyze loan agreements, bank documents, and EMI papers with deep expertise in:
- Indian and international banking regulations
- Hidden clauses and penalty structures  
- Risk assessment and financial impact analysis
- Plain-language explanation of legal/financial jargon

Always be precise, helpful, and protective of the borrower's interests.
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
Analyze the provided loan document text in its entirety to generate a high-fidelity, synchronized audit.
Identify all loan structures, hidden trap clauses, risk assessments, jargon explanations, suspicious markers, and trust metrics.

DOCUMENT TEXT:
{safe_text}

You must return a single JSON object containing exactly this structure, with no extra text or explanations. Ensure all numeric amounts are parsed as numbers:

{{
  "core_info": {{
    "loan_type": "string (e.g. Home Loan, Personal Loan, Car Loan, Business Loan)",
    "lender_name": "string (name of the financial institution)",
    "borrower_name": "string (full name of borrower)",
    "loan_amount": "string (formatted amount, e.g. ₹50,00,000)",
    "loan_amount_numeric": 5000000,
    "interest_rate": "string (interest rate, e.g. 8.5% p.a.)",
    "interest_rate_numeric": 8.5,
    "interest_type": "Fixed / Floating / Mixed / Not specified",
    "tenure": "string (e.g. 20 years)",
    "tenure_months": 240,
    "emi_amount": "string (estimated monthly EMI, e.g. ₹43,391)",
    "emi_numeric": 43391,
    "processing_fee": "string (processing charges, e.g. ₹10,000)",
    "document_date": "string (e.g. 18 May 2026)",
    "summary": "3-4 sentence expert plain-English summary of this loan document structure, highlighting key structural caveats.",
    "document_quality": "Clear / Partially Clear / Unclear"
  }},
  "hidden_traps": [
    {{
      "id": 1,
      "title": "Short descriptive title of the trap (e.g., Unilateral Floating Margin Clause)",
      "severity": "Critical / High / Medium / Low",
      "original_text": "Exact quote or close paraphrase of the relevant contract clause",
      "plain_explanation": "What this means in simple, everyday language",
      "impact": "Concrete financial penalty or risk the borrower faces (e.g., specific rupee increase or credit impact)",
      "advice": "Actionable advice or specific negotiation question the borrower can ask"
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

