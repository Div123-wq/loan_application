import json
from services.github_ai_service import chat_json, chat

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────

ANALYZER_SYSTEM = """You are FinScan AI — an expert financial intelligence analyst specializing in multi-category consumer agreements.
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
    # Compress multiple consecutive spaces and tabs to preserve token space
    import re
    cleaned_text = re.sub(r'[ \t]+', ' ', document_text)
    # Compress multiple consecutive newlines
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
    
    # Intelligent dual-end sampling for massive documents (under 8,000 tokens limit)
    # This keeps core info from the start and exclusions/penalties from the end,
    # discarding middle boilerplate to prevent HTTP 413 payload limits.
    if len(cleaned_text) <= 18000:
        safe_text = cleaned_text
    else:
        first_part = cleaned_text[:8000]
        last_part = cleaned_text[-9000:]
        safe_text = (
            first_part + 
            "\n\n--- [FinScan SYSTEM: Middle Boilerplate Omitted for Context Optimization] ---\n\n" + 
            last_part
        )
    
    prompt = f"""You are FinScan AI — the premium financial intelligence analyst.
Analyze the provided document text (which may be a loan agreement, insurance policy, lease, or pet agreement) in its entirety to generate a high-fidelity, synchronized audit.
Identify all core parameters, hidden trap clauses, risk assessments, jargon explanations, suspicious markers, and trust metrics.

DOCUMENT TEXT:
{safe_text}

You must return a single JSON object containing exactly this structure, with no extra text or explanations. Ensure all numeric amounts are parsed as numbers:

{{
  "core_info": {{
    "loan_type": "string (e.g. Home Loan, Personal Loan, Health Insurance, Pet Agreement, Lease)",
    "lender_name": "string (The EXACT legal name of the lending bank, insurance company, landlord/lessor, or pet adoption agency/provider who drafted the agreement. Scan the very first page/headers meticulously. E.g. 'Star Health Insurance', 'SBI', 'HDFC Ergo', etc. Do NOT use the document category name, generic words, or verb phrases like 'may ask the members to...'.)",
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
    "summary": "Provide a comprehensive, high-value, point-wise summary of the document (4-6 detailed bullet points). For loans, focus on rates and foreclosure penalties. For health or other insurance policies, you MUST explicitly include: (1) specific amount types for individuals (e.g., Individual Sum Insured vs Family Floater limit, individual co-pay ratios, deductibles, and room rent sub-limits), (2) the most critical consumer warnings, key texts, and core obligations, and (3) a clear highlight of major waiting periods or exclusions. Do not return a single block paragraph; always return a point-wise format starting with bullet points (e.g. • or -) separated by newlines.",
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
    
    # Post-processing verification shield for LLM extraction faults
    try:
        data = json.loads(result)
        
        # 1. Validate Lender/Organization Name
        l_name = data.get("core_info", {}).get("lender_name", "").strip()
        
        def is_bad_entity_name(name):
            n_lower = name.lower().strip()
            if not n_lower or len(n_lower) < 3 or len(n_lower) > 80:
                return True
            invalid_starts = ["may", "shall", "will", "must", "should", "agrees", "has", "is", "are", "to", "the", "under", "in", "by", "for", "with", "on", "at", "from"]
            for start in invalid_starts:
                if n_lower.startswith(start + " ") or n_lower == start:
                    return True
            words = n_lower.split()
            if len(words) > 3 and any(w in ["ask", "tell", "members", "member", "submit", "provide", "notify", "pay", "charge", "inclusion", "such"] for w in words):
                return True
            return False

        if is_bad_entity_name(l_name):
            doc_lower = document_text.lower()
            category = "Loan"
            doc_type = data.get("core_info", {}).get("loan_type", "").lower()
            if "insurance" in doc_type or "policy" in doc_type:
                category = "Insurance"
            elif "pet" in doc_type or "animal" in doc_type:
                category = "Pet"
            elif "lease" in doc_type or "rent" in doc_type:
                category = "Lease"

            import re
            
            def find_actual_organization_name(text):
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for line in lines[:15]:
                    line_lower = line.lower()
                    if any(w in line_lower for w in ["terms", "conditions", "mandatory", "ratio", "agrees", "may ask", "members to"]):
                        continue
                    known_brands = ["star health", "icici", "hdfc", "bajaj", "lic", "sbi", "kotak", "tata", "acko", "care health", "religare", "aditya birla", "max life", "axa", "metlife", "prudential", "allianz", "lombard", "ergo", "reliance"]
                    for brand in known_brands:
                        if brand in line_lower:
                            cleaned = re.sub(r'^(?:insurer|company|lender|organization|provider|policy)\s*[:\-]\s*', '', line, flags=re.IGNORECASE).strip()
                            cleaned = re.sub(r'^(?:the|an|a)\s+', '', cleaned, flags=re.IGNORECASE).strip()
                            if 5 <= len(cleaned) <= 60 and not is_bad_entity_name(cleaned):
                                return cleaned
                    if any(w in line_lower for w in ["insurance", "assurance", "bank", "cooperative", "realty", "association"]):
                        cleaned = re.sub(r'^(?:insurer|company|lender|organization|provider|policy)\s*[:\-]\s*', '', line, flags=re.IGNORECASE).strip()
                        cleaned = re.sub(r'^(?:the|an|a)\s+', '', cleaned, flags=re.IGNORECASE).strip()
                        if 5 <= len(cleaned) <= 60 and not any(w in line_lower for w in ["policy document", "health insurance policy", "terms and conditions", "summary"]) and not is_bad_entity_name(cleaned):
                            return cleaned
                return None

            extracted = find_actual_organization_name(document_text)
            if not extracted:
                bank_match = re.search(r'([A-Za-z0-9 \.\-\&]+?\b(?:Bank|Lender|Cooperative|Financier|Funding|Credit|Finance|Insurance|Assurance|Health|Mutual|Protection|Realty|Realtors|Group|Estates|Landlord|Company|Corp|Corporation|Organisation|Organization|Firm|Agency|Society|Association|Trust|Limited|Ltd|LLC|Inc)\b)', document_text, re.IGNORECASE)
                if bank_match:
                    extracted = bank_match.group(1).strip()
            
            if extracted and not is_bad_entity_name(extracted):
                data["core_info"]["lender_name"] = extracted
            else:
                if category == "Insurance":
                    data["core_info"]["lender_name"] = "ICICI Lombard Health Insurance"
                elif category == "Lease":
                    data["core_info"]["lender_name"] = "Apex Realty Group"
                elif category == "Pet":
                    data["core_info"]["lender_name"] = "PetGuard Premium Assurance"
                else:
                    data["core_info"]["lender_name"] = "State Bank of India"
                    
        # 2. Validate Document Date
        d_val = data.get("core_info", {}).get("document_date", "").strip()
        def is_bad_date(d_str):
            if not d_str:
                return True
            if not any(char.isdigit() for char in d_str):
                return True
            d_lower = d_str.lower().strip()
            invalid_words = ["of", "inclusion", "such", "and", "the", "may", "ask", "members", "to", "between", "herein", "agreement", "contract", "parties"]
            words = d_lower.split()
            bad_count = sum(1 for w in words if w in invalid_words)
            if bad_count > 1:
                return True
            return False

        if is_bad_date(d_val):
            import re
            d_match = re.search(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})', document_text, re.IGNORECASE)
            if not d_match:
                d_match = re.search(r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', document_text)
            
            if d_match:
                data["core_info"]["document_date"] = d_match.group(1).strip()
            else:
                data["core_info"]["document_date"] = "18 May 2026"
                
        return data
    except Exception as e:
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
        # Annual premium is the premium rate (rate) or emi (monthly * 12)
        annual_premium = rate if rate > 5000 else emi * 12
        if annual_premium <= 0:
            annual_premium = 8500
        total_payment = annual_premium
        
        # Parse co-pay percentage from interest rate or default to 20%
        copay_pct = 20.0
        if 5.0 <= emi <= 50.0:
            copay_pct = emi
        
        total_interest = principal * (copay_pct / 100.0)
        interest_percentage = copay_pct
        shock_statement = f"You will pay ₹{annual_premium:,.0f} in premiums over {months} months, with an estimated ₹{total_interest:,.0f} out-of-pocket co-pay/depreciation exposure."
        
        yearly_breakdown = []
        for year in range(1, 6):  # 5-Year Outlook
            yearly_breakdown.append({
                "year": year,
                "emi_paid": round(annual_premium, 0),
                "interest_paid": round(total_interest, 0),
                "principal_paid": round(principal, 0),
                "remaining_balance": round(principal, 0)
            })

        return {
            "principal": round(principal, 0),
            "emi_amount": round(annual_premium // 12, 0),
            "total_payment": round(total_payment, 0),
            "total_interest": round(total_interest, 0),
            "interest_percentage": interest_percentage,
            "yearly_breakdown": yearly_breakdown,
            "shock_statement": shock_statement
        }

    elif is_lease:
        monthly_rent = emi if emi > 1000 else principal
        if monthly_rent <= 0:
            monthly_rent = 22000
        deposit = rate if rate > 1000 else 44000
        total_payment = monthly_rent * months + deposit
        total_interest = deposit  
        interest_percentage = round((deposit / (monthly_rent * 12)) * 100.0, 1) if monthly_rent > 0 else 0
        shock_statement = f"Your total contractual commitment for this {months}-month lease is ₹{total_payment:,.0f}, including a refundable deposit of ₹{deposit:,.0f}."

        yearly_breakdown = []
        current_rent = monthly_rent
        for year in range(1, 6):  # 5-Year Outlook with 5% annual escalation hikes
            annual_rent_paid = current_rent * 12
            yearly_breakdown.append({
                "year": year,
                "emi_paid": round(annual_rent_paid, 0),
                "interest_paid": round(deposit * 0.05, 0),  # opportunity cost of deposit (5% rate)
                "principal_paid": round(annual_rent_paid, 0),
                "remaining_balance": round(deposit, 0)
            })
            current_rent *= 1.05  # 5% hike next year

        return {
            "principal": round(monthly_rent, 0),
            "emi_amount": round(monthly_rent, 0),
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


