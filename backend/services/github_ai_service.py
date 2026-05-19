import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        token = os.environ.get("GITHUB_TOKEN")
        if not token or token == "your_github_pat_here":
            return None
        _client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=token,
        )
    return _client

def get_model():
    return os.environ.get("GITHUB_MODEL", "gpt-4o")

def chat(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Send a chat request to GitHub Models, or fallback to an intelligent mock advisor if no token or error."""
    client = get_client()
    if client is None:
        return get_mock_chat_response(user_prompt)

    model = get_model()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling GitHub AI Service (falling back to mock): {e}")
        return get_mock_chat_response(user_prompt)

def chat_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Send a chat request and request JSON output, or fallback to mock JSON if no token or error."""
    client = get_client()
    if client is None:
        return get_mock_json_response(user_prompt)

    model = get_model()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt + "\n\nRespond ONLY with valid JSON."},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content.strip()
        
        # Strip Markdown blocks if they exist
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        # Fallback to finding the first { and last } if it's still messy
        if content.find('{') != -1 and content.rfind('}') != -1:
            content = content[content.find('{'):content.rfind('}')+1]
            
        return content.strip()
    except Exception as e:
        print(f"Error calling GitHub AI Service JSON (falling back to mock): {e}")
        return get_mock_json_response(user_prompt)


# ─────────────────────────────────────────────
# INTELLIGENT MOCK RESPONSES FOR DEMO MODE
# ─────────────────────────────────────────────

def get_mock_chat_response(prompt: str) -> str:
    """Returns dynamic, helpful mock responses when API token is not supplied."""
    p_lower = prompt.lower()
    
    if "dangerous" in p_lower or "trap" in p_lower or "risk" in p_lower:
        return "Yes, this loan has a couple of elements that could become dangerous. The biggest risk is the floating rate clause linked to MCLR. If benchmark rates rise, the bank can unilaterally increase your interest rate and your monthly EMI will jump without warning. Additionally, there is a high 2% foreclosure penalty fee that prevents you from easily switching to a cheaper lender later."
        
    if "miss" in p_lower or "late" in p_lower or "penalty" in p_lower:
        return "If you miss or delay a payment, the bank will charge an additional penal interest rate of 2% per month (24% per year) compounded on outstanding arrears. More importantly, missing payments will trigger an immediate reporting to credit bureaus, dropping your credit rating by 50-80 points, which makes future loans far more expensive."
        
    if "negotiate" in p_lower or "bargain" in p_lower:
        return "You have excellent leverage to negotiate terms before signing! Ask the bank to fully waive the flat INR 15,000 administrative levy (since you are already paying standard processing charges). You should also bargain to cap the floating rate margin adjustment at 1% per year, and request a waiver of foreclosure penalties after year 3."

    # General friendly companion response
    return "That's a very standard clause in home loan agreements! It essentially means you are responsible for maintaining property insurance with the bank named as the primary beneficiary. If you'd like to look at potential trap clauses or negotiate terms, check out the tabs on the left sidebar!"


def get_mock_json_response(prompt: str) -> str:
    """Intelligent dynamic mock JSON analyzer for fallback/demo mode.
    Parses the actual prompt text, detects document type, extracts parameters,
    and dynamically compiles high-fidelity reports for loans, leases, pets, and insurances.
    """
    import re
    p_lower = prompt.lower()

    # ── Step 1: Extract actual document text ─────────────────────────
    doc_text = ""
    if "document text:" in p_lower:
        parts = prompt.split("DOCUMENT TEXT:")
        if len(parts) > 1:
            doc_text = parts[1]
            if "you must return a single json object" in doc_text.lower():
                doc_text = re.split(r'(?i)you must return a single json object', doc_text)[0]
            doc_text = doc_text.strip()
    if not doc_text:
        doc_text = prompt

    doc_lower = doc_text.lower()

    # ── Step 2: Detect Category ──────────────────────────────────────
    # Avoid substring matches like "cat" matching "application" or "communication"
    pet_words = [r"\bpet\b", r"\bdog\b", r"\bcat\b", r"\bveterinary\b", r"\banimal\b", r"\badoption\b", r"\bbreed\b"]
    ins_words = [r"\bpolicy\b", r"\binsurance\b", r"\binsurer\b", r"\binsured\b", r"\bdeductible\b", r"\bpremium\b", r"\bcopay\b"]
    lease_words = [r"\blease\b", r"\btenant\b", r"\blandlord\b", r"\brent\b", r"\bsecurity deposit\b", r"\bpremises\b", r"\blessor\b", r"\blessee\b"]
    
    if any(re.search(pat, doc_lower) for pat in pet_words):
        category = "Pet"
    elif any(re.search(pat, doc_lower) for pat in ins_words):
        category = "Insurance"
    elif any(re.search(pat, doc_lower) for pat in lease_words):
        category = "Lease"
    else:
        category = "Loan"

    # ── Step 3: Local Parameter Extractor ────────────────────────────
    lender_name = "State Bank of India"
    document_date = "18 May 2026"
    borrower_name = "Rohan Sharma"

    # Try to find date
    date_match = re.search(r'(?:date|dated|on this|entered into on)\s*([A-Za-z0-9 \.,]{6,25})', doc_text, re.IGNORECASE)
    if date_match:
        document_date = date_match.group(1).strip()
    else:
        date_match2 = re.search(r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})', doc_text)
        if date_match2:
            document_date = date_match2.group(1)

    # Universal currency amount helper — matches BOTH ₹X,XX,XXX AND X,XX,XXX INR
    def extract_amount(label_pattern, text):
        """Returns digit string (no commas) or None if not found."""
        m = re.search(
            label_pattern +
            r'[^\n]{0,80}?(?:(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)|([\d,]+(?:\.\d{1,2})?)\s*(?:INR|Rs\.?))',
            text, re.IGNORECASE | re.DOTALL
        )
        if m:
            return (m.group(1) or m.group(2)).replace(',', '')
        return None

    # Universal large amount fallback if no label matched
    def extract_large_amount_fallback(text):
        m = re.findall(r'(?:₹|Rs\.?|INR)\s*([\d,]{5,10})|([\d,]{5,10})\s*(?:INR|Rs\.?)', text, re.IGNORECASE)
        for group1, group2 in m:
            val = (group1 or group2).replace(',', '')
            if val.isdigit() and int(val) >= 10000:
                return val
        return None

    def fmt_inr(n):
        """Format integer as Indian-style currency string: ₹5,00,000"""
        n = int(float(n))
        s = str(n)
        if len(s) <= 3:
            return f'\u20b9{s}'
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.append(rest)
        groups.reverse()
        return '\u20b9' + ','.join(groups) + ',' + last3

    # Dynamic universal name extraction
    l_match = re.search(r'(?:lender|bank|financial institution|lessor|landlord|insurer|provider|company)(?:\s+name)?\s*[:\-]?\s*([A-Za-z][A-Za-z0-9 \.,]{3,50})', doc_text, re.IGNORECASE)
    if l_match:
        lender_name = l_match.group(1).split('\n')[0].strip()
    else:
        bank_match = re.search(r'([A-Za-z0-9 \.\-]+?\b(?:Bank|Lender|Cooperative|Financier|Funding|Credit|Finance|Insurance|Assurance|Health|Mutual|Protection|Realty|Realtors|Group|Estates|Landlord)\b)', doc_text, re.IGNORECASE)
        if bank_match:
            lender_name = bank_match.group(1).strip()

    b_match = re.search(r'(?:borrower|applicant|customer|tenant|lessee|policyholder|insured|beneficiary)(?:\s+name)?\s*[:\-]?\s*([A-Za-z][A-Za-z ]{3,40})', doc_text, re.IGNORECASE)
    if b_match:
        borrower_name = b_match.group(1).split('\n')[0].strip()

    if category == "Pet":
        if lender_name == "State Bank of India":
            lender_name = "PetGuard Premium Assurance"
        loan_amount = "₹10,00,000"
        loan_amount_numeric = 1000000
        interest_rate = "₹1,250 / mo"
        interest_rate_numeric = 1250
        interest_type = "Fixed Premium"
        tenure = "12 Months"
        tenure_months = 12
        emi_amount = "₹1,250"
        emi_numeric = 1250
        processing_fee = "₹500 Co-registration Fee"

        cov_raw = extract_amount(r'(?:coverage|coverage limit|sum|amount|limit)', doc_text)
        if not cov_raw:
            cov_raw = extract_large_amount_fallback(doc_text)
        if cov_raw:
            loan_amount = fmt_inr(cov_raw)
            loan_amount_numeric = int(float(cov_raw))
        pr_raw = extract_amount(r'(?:premium|monthly fee|fee)', doc_text)
        if pr_raw:
            val = int(float(pr_raw))
            interest_rate = fmt_inr(val) + " / mo"
            interest_rate_numeric = val
            emi_amount = fmt_inr(val)
            emi_numeric = val

    elif category == "Insurance":
        if lender_name == "State Bank of India":
            lender_name = "StarCare Health Insurance"
        loan_amount = "₹5,00,000"
        loan_amount_numeric = 500000
        interest_rate = "₹8,500 / yr"
        interest_rate_numeric = 8500
        interest_type = "Insurance Policy"
        tenure = "Annual Cover"
        tenure_months = 12
        emi_amount = "₹708 / mo"
        emi_numeric = 708
        processing_fee = "₹1,000 Administration Fee"

        si_raw = extract_amount(r'(?:sum insured|sum assured|coverage|insured amount|policy amount|cover amount|total cover)', doc_text)
        if not si_raw:
            si_raw = extract_large_amount_fallback(doc_text)
        if si_raw:
            loan_amount = fmt_inr(si_raw)
            loan_amount_numeric = int(float(si_raw))

        pr_raw = extract_amount(r'(?:annual premium|yearly premium|premium amount|premium|amount due|amount payable)', doc_text)
        if pr_raw:
            val = int(float(pr_raw))
            if val > 5000:
                interest_rate = fmt_inr(val) + ' / yr'
                interest_rate_numeric = val
                emi_amount = fmt_inr(val // 12) + ' / mo'
                emi_numeric = val // 12
            else:
                interest_rate = fmt_inr(val) + ' / mo'
                interest_rate_numeric = val
                emi_amount = fmt_inr(val) + ' / mo'
                emi_numeric = val

    elif category == "Lease":
        if lender_name == "State Bank of India":
            lender_name = "Apex Realty Group"
        loan_amount = "₹22,000 / mo"
        loan_amount_numeric = 22000
        interest_rate = "₹44,000 Deposit"
        interest_rate_numeric = 44000
        interest_type = "Fixed Rental Schedule"
        tenure = "11 Months"
        tenure_months = 11
        emi_amount = "₹22,000"
        emi_numeric = 22000
        processing_fee = "₹2,500 Registration charges"

        r_raw = extract_amount(r'(?:monthly rent|rent amount|rent)', doc_text)
        if r_raw:
            val = int(float(r_raw))
            loan_amount = fmt_inr(val) + ' / mo'
            loan_amount_numeric = val
            emi_amount = fmt_inr(val)
            emi_numeric = val
        dp_raw = extract_amount(r'(?:security deposit|deposit)', doc_text)
        if dp_raw:
            interest_rate = fmt_inr(int(float(dp_raw))) + ' Deposit'
            interest_rate_numeric = float(dp_raw)

    else:  # Loan
        loan_amount = "₹50,00,000"
        loan_amount_numeric = 5000000
        interest_rate = "8.5% p.a."
        interest_rate_numeric = 8.5
        interest_type = "Floating"
        tenure = "20 Years"
        tenure_months = 240
        emi_amount = "₹43,391"
        emi_numeric = 43391
        processing_fee = "₹10,000"

        pa_raw = extract_amount(r'(?:loan amount|principal amount|principal|sanctioned amount)', doc_text)
        if not pa_raw:
            pa_raw = extract_large_amount_fallback(doc_text)
        if pa_raw:
            loan_amount = fmt_inr(pa_raw)
            loan_amount_numeric = int(float(pa_raw))
        rt_match = re.search(r'(?:interest rate|rate of interest|rate)\s*[:\-]?\s*([\d\.]+)\s*%', doc_text, re.IGNORECASE)
        if rt_match:
            interest_rate = rt_match.group(1) + '% p.a.'
            interest_rate_numeric = float(rt_match.group(1))
        emi_raw = extract_amount(r'(?:emi|monthly installment|monthly instalment|monthly payment)', doc_text)
        if emi_raw:
            emi_amount = f'\u20b9{int(float(emi_raw)):,}'
            emi_numeric = int(float(emi_raw))

    # Helper: pull a verbatim sentence from doc containing all keywords
    def find_verbatim_quote(keywords, default_quote):
        sentences = re.split(r'[\.\n\r]+', doc_text)
        for s in sentences:
            s_clean = s.strip()
            if 15 < len(s_clean) < 300:
                s_lower = s_clean.lower()
                if all(kw in s_lower for kw in keywords):
                    return s_clean
        # Secondary soft-matching pass
        for s in sentences:
            s_clean = s.strip()
            if 20 < len(s_clean) < 300:
                s_lower = s_clean.lower()
                if any(kw in s_lower for kw in keywords) and any(modal in s_lower for modal in ["shall", "must", "will", "agrees", "reserves", "charge", "fee", "penalty"]):
                    return s_clean
        return default_quote

    # ── Step 4: Handle Comparison Battle Route ───────────────────────
    if "compare" in p_lower or "winner_cheapest" in p_lower or "winner" in p_lower:
        if category == "Pet":
            winner = "PetGuard Premium Assurance"
            insight1 = "₹3,500 lower annual deductible outlay"
            insight2 = "Fewer exclusions (3 exclusions vs 5 exclusions in PetFirst)"
        elif category == "Insurance":
            winner = "StarCare General Insurance"
            insight1 = "No room rent sub-limits"
            insight2 = "Cheaper premium plan (₹1,850/mo vs ₹2,400/mo)"
        elif category == "Lease":
            winner = "Apex Realty Group"
            insight1 = "Slightly cheaper rent than surrounding options"
            insight2 = "Security deposit capped at 2 months' rent"
        else:
            winner = "SBI Home Loan"
            insight1 = "₹50,000 cheaper overall upfront fees"
            insight2 = "No exit prepayment charges after Year 3"

        return json.dumps({
          "winner_cheapest": {
            "doc_id": "mock_id_1",
            "reason": f"This option represents the lowest overall financial cost of ₹{loan_amount_numeric:,.0f} and most lenient penalty resets."
          },
          "winner_safest": {
            "doc_id": "mock_id_2",
            "reason": "Alternative comparison plan contains fewer hidden traps and caps annual escalations securely."
          },
          "winner_overall": {
            "doc_id": "mock_id_1",
            "reason": "Recommended overall based on superior cost-efficiency metrics and low risk profiles."
          },
          "comparison_table": [
            { "category": "Base Cost", "winner": winner, "insight": insight1 },
            { "category": "Risk Index", "winner": winner, "insight": insight2 }
          ],
          "radar_scores": {
            "labels": ["Cost Efficiency", "Exclusion Safety", "Transparency", "Flexibility", "Terms Ratio"],
            "datasets": [
              { "label": "This Document", "data": [85, 75, 80, 70, 75] },
              { "label": "Market Competitor", "data": [70, 60, 75, 55, 65] }
            ]
          },
          "negotiation_tips": [
            "Request standard waiver of administrative fee processing charges.",
            "Ask to cap the maximum annual escalations at 5%."
          ],
          "final_verdict": f"The analyzed {category} contract is superior to market alternatives because it maintains more reasonable default conditions and shields you from excessive initial expenses."
        })

    # ── Step 5: Handle Negotiation Script Route ──────────────────────
    if "negotiate" in p_lower or "negotiable_terms" in p_lower:
        if category == "Pet":
            term1, curr1, neg1 = "Pre-existing exclusion", "Full Exclusion", "Registered clearance waiver"
            term2, curr2, neg2 = "Annual premium adjust", "Unilateral revisions", "Cap adjustments at 8% p.a."
            script = "I noticed the policy includes unilateral premium increases. Can we cap the annual adjustment rate at 8% maximum?"
        elif category == "Insurance":
            term1, curr1, neg1 = "Specialist Co-payment", "20% co-pay ratio", "0% co-payment plan option"
            term2, curr2, neg2 = "Room Rent Sub-limits", "1% Sum Insured cap", "No Room Rent caps plan"
            script = "I would like to explore options with no co-payment for specialist hospitalizations. What premium adjustment is required for a 0% co-pay?"
        elif category == "Lease":
            term1, curr1, neg1 = "Wear-and-tear Deductions", "Uncapped paint/cleaning", "Normal wear-and-tear excluded"
            term2, curr2, neg2 = "Eviction Notification", "7-day termination", "Standard 30-day notice"
            script = "The 7-day termination notice is quite short. Could we revise this to a standard 30-day or 60-day notification period for safety?"
        else:
            term1, curr1, neg1 = "Administrative Levy", "INR 15,000 flat charges", "Complete waiver"
            term2, curr2, neg2 = "Prepayment Penalty", "2% penalty exit fee", "Waiver of exit fees after Year 3"
            script = "Could we completely waive the flat INR 15,000 administrative levy since I am already paying standard upfront processing fees?"

        return json.dumps({
          "negotiable_terms": [
            { "term": term1, "current": curr1, "negotiable_to": neg1, "success_probability": "High", "how_to_ask": "Request a waiver as a high-value customer." },
            { "term": term2, "current": curr2, "negotiable_to": neg2, "success_probability": "Medium", "how_to_ask": "Mention industry standards." }
          ],
          "questions_for_bank": [f"Is the {term1} negotiable?", f"Can we alter the {term2} clause?"],
          "best_time_to_negotiate": "Before executing final signatures",
          "leverage_points": ["Excellent baseline credit credentials and history."],
          "red_lines": ["Unilateral termination options with under 15 days notice."],
          "negotiation_script": script
        })

    # ── Step 6: Handle Pressure / Amortization Stress Route ──────────
    if "pressure" in p_lower or "stress_level" in p_lower:
        salary = 120000.0
        expenses = 45000.0
        family_size = 3
        obligations = "Standard outlays"

        sal_match = re.search(r"Monthly Salary: ₹([\d,]+)", prompt)
        if sal_match: salary = float(sal_match.group(1).replace(",", ""))
        exp_match = re.search(r"Monthly Expenses: ₹([\d,]+)", prompt)
        if exp_match: expenses = float(exp_match.group(1).replace(",", ""))
        fam_match = re.search(r"Family Size: (\d+)", prompt)
        if fam_match: family_size = int(fam_match.group(1))

        monthly_surplus = salary - expenses
        emi_to_income_ratio = round((emi_numeric / salary * 100.0), 1) if salary > 0 else 30.0

        # Dynamic stress scoring
        net_margin = salary - expenses - emi_numeric
        if net_margin < 0:
            stress_score = min(98, 70 + int(abs(net_margin) / 1000.0) * 3)
        else:
            stress_score = max(10, 60 - int(net_margin / 2000.0) * 2)
        stress_score = min(max(stress_score + family_size * 3, 10), 99)

        stress_level = "Critical Risk" if stress_score >= 80 else "High Risk" if stress_score >= 60 else "Medium Risk" if stress_score >= 40 else "Low Risk"

        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        monthly_calendar = []
        danger_months = []
        safe_months = []
        for m in months_list:
            m_lower = m.lower()
            m_stress = "Low"
            m_note = "Normal baseline flow"

            if m_lower == "march":
                m_stress = "High" if stress_score > 50 else "Medium"
                m_note = "Tax payments and audit outlays"
                if m_stress == "High": danger_months.append(m)
            elif m_lower == "october":
                m_stress = "High" if stress_score > 40 else "Medium"
                m_note = "Festivals and high seasonal spending"
                if m_stress == "High": danger_months.append(m)
            else:
                if stress_score > 70:
                    m_stress = "Medium"
                    m_note = "Tight baseline surplus"
                else:
                    safe_months.append(m)

            monthly_calendar.append({ "month": m, "stress": m_stress, "note": m_note })

        return json.dumps({
          "monthly_surplus": monthly_surplus,
          "emi_to_income_ratio": emi_to_income_ratio,
          "stress_level": stress_level,
          "stress_score": stress_score,
          "monthly_calendar": monthly_calendar,
          "danger_months": danger_months,
          "safe_months": safe_months,
          "lifestyle_impact": f"Ensure your monthly dynamic cash flows absorb the ₹{emi_numeric:,.0f} commitment.",
          "breaking_point_months": max(2, int(monthly_surplus / max(1, emi_numeric))),
          "breaking_point_note": f"A savings pool covers about {max(2, int(monthly_surplus / max(1, emi_numeric)))} months of direct stress.",
          "recommendations": ["Establish a 3-month cash reserve.", "Minimize high-interest credit card debt."],
          "verdict": f"The monthly commitments require ₹{emi_numeric:,.0f}. Your cash surplus yields a {stress_level.lower()} rating overall."
        })

    # ── Step 7: Handle Simulator Route ───────────────────────────────
    if "simulate" in p_lower or "timeline_effects" in p_lower:
        scenario = "What if payments are missed?"
        scen_match = re.search(r'borrower is asking: "(.*?)"', prompt)
        if scen_match: scenario = scen_match.group(1)

        s_lower = scenario.lower()
        if "miss" in s_lower or "late" in s_lower or "default" in s_lower or "delay" in s_lower:
            penalty_amount = "2% penal interest per month"
            extra_interest = "₹5,000"
            total_extra_cost = "₹8,500"
            credit_score_impact = "-50 to -80 points (Substantial Drop)"
            plain_summary = "Missing or delaying commitments triggers immediate compound interest adjustments and bureau credit score downgrades."
        else:
            penalty_amount = "₹0"
            extra_interest = "₹0"
            total_extra_cost = "₹0"
            credit_score_impact = "None"
            plain_summary = f"The scenario '{scenario}' reviewed has normal compliance and will not result in critical financial penalties."

        return json.dumps({
          "scenario": scenario,
          "immediate_impact": {
            "penalty_amount": penalty_amount,
            "extra_interest": extra_interest,
            "total_extra_cost": total_extra_cost
          },
          "timeline_effects": [
            { "month": 1, "event": "Late fees applied", "cost": "₹2,500", "severity": "medium" },
            { "month": 2, "event": "Credit Bureau notified", "cost": "₹0", "severity": "high" }
          ],
          "credit_score_impact": credit_score_impact,
          "total_extra_payment": total_extra_cost,
          "recovery_timeline": "6 Months",
          "bank_action_risk": "Medium",
          "advice": ["Submit written clarification to the provider.", "Pay off the outstanding balance quickly."],
          "severity_level": "High",
          "plain_summary": plain_summary
        })

    # ── Step 8: Handle Milestones / Panics Route ─────────────────────
    if "deadline" in p_lower or "upcoming_milestones" in p_lower:
        return json.dumps({
          "upcoming_milestones": [
            { "date": "2027-05-18", "event": "Anniversary Review Cycle", "type": "milestone", "financial_note": "Amortization schedule updates. Dynamic rates spread will be audited." }
          ],
          "panic_periods": [
            { "period": "June 2027", "reason": "Seasonal expenditures peak concurrently.", "risk_level": "Medium", "estimated_shortfall": "₹10,000", "advice": "Set aside extra cash reserves starting now." }
          ],
          "5_year_forecast": { "easy_years": [1], "challenging_years": [3], "reason": "Exclusion timelines and reset periods trigger adjustments." },
          "smart_tip": "Keep a small cash buffer in a designated reserve account."
        })

    # ── Step 9: Consolidated Master Audit Fallback ───────────────────
    # We construct highly targeted hidden traps by scanning actual document text
    # for verbatim quotes matching the detected category.
    if category == "Pet":
        summary = f"This {lender_name} Pet Policy covers basic veterinary healthcare up to {loan_amount}. However, it contains typical breed-specific congenital exclusions, pre-existing health exclusions, and reserves the right to increase monthly premiums unilaterally."
        
        q1 = find_verbatim_quote(["condition", "exclude"], "Pre-existing veterinary health conditions or chronic illnesses prior to policy registration are strictly excluded from all coverages.")
        q2 = find_verbatim_quote(["hereditary", "exclude"], "Hereditary conditions, structural joint issues, and congenital pet defects are not subject to basic premium reimbursements.")
        q3 = find_verbatim_quote(["premium", "increase"], "The provider reserves the absolute right to adjust monthly pet premiums annually based on claims frequency and age brackets.")

        hidden_traps = [
            {
                "id": 1, "severity": "Critical", "title": "Pre-Existing Conditions Exclusion",
                "original_text": q1,
                "plain_explanation": "Any illness or injury your pet showed symptoms of before buying this policy is never covered.",
                "impact": "You must pay 100% of vet costs for pre-existing issues, costing you ₹30,000+ for recurring treatments.",
                "advice": "Get a complete veterinary clearance document before purchase to prove what is currently a healthy status."
            },
            {
                "id": 2, "severity": "High", "title": "Hereditary Joint Exclusions",
                "original_text": q2,
                "plain_explanation": "Diseases common to your dog/cat breed (like hip dysplasia in Retrievers) are not covered.",
                "impact": "Joint surgeries or breed-specific hereditary medical bills of up to ₹60,000 must be paid out-of-pocket.",
                "advice": "Ask the agency to add a custom breed-specific waiver rider."
            },
            {
                "id": 3, "severity": "Medium", "title": "Unilateral Premium Hikes",
                "original_text": q3,
                "plain_explanation": "The provider can raise your premium rate next year without your permission if claims rise.",
                "impact": "Your monthly outlays will spike by ₹10,000+ annually as your pet gets older.",
                "advice": "Choose providers offering a locked-premium structure or annual rate caps under 10%."
            }
        ]
        friendly_explanations = [
            { "legal_text": "Exclusion of congenital anomalies.", "friendly_text": "Issues your pet is born with are not covered.", "emoji": "🐕", "category": "Insurance" }
        ]
        verdict = "This pet assurance document offers standard vet coverage, but heavily limits protection for pre-existing or breed-specific diseases. Ensure medical history is fully cleared."
        top_risk = "Pre-existing health exclusion clause that voids chronic coverage."
        flag = "Unilateral Premium Spreads"
        flag_reason = "Enables unlimited annual increases in premiums."
        flag_orig = q3

    elif category == "Insurance":
        # Dynamic Sub-Type Detection for Insurance
        insurance_sub_type = "Health Insurance"  # default
        auto_words = [r"\bcar\b", r"\bvehicle\b", r"\bauto\b", r"\bmotor\b", r"\bdriving\b", r"\bcollision\b", r"\bgarage\b", r"\broadside\b", r"\baccident\b"]
        life_words = [r"\blife\b", r"\bdeath\b", r"\bbeneficiary\b", r"\bsurrender\b", r"\bterm\b", r"\bmortality\b", r"\bnominee\b"]
        prop_words = [r"\bproperty\b", r"\bhome\b", r"\bbuilding\b", r"\bdwelling\b", r"\bfire\b", r"\btheft\b", r"\bsubsidence\b", r"\bstructure\b"]

        if any(re.search(pat, doc_lower) for pat in auto_words):
            insurance_sub_type = "Auto Insurance"
        elif any(re.search(pat, doc_lower) for pat in life_words):
            insurance_sub_type = "Life Insurance"
        elif any(re.search(pat, doc_lower) for pat in prop_words):
            insurance_sub_type = "Property Insurance"

        if insurance_sub_type == "Auto Insurance":
            summary = (
                f"This comprehensive motor policy from {lender_name} offers a coverage sum of {loan_amount} for own damage and third-party liabilities. "
                f"Crucially, it enforces a steep depreciation schedule on plastic, nylon, and rubber components, meaning you will face up to 50% out-of-pocket costs for parts during repairs. "
                f"Additionally, cashless repairs are strictly limited to network garages, and minor independent claims are subject to a high compulsory deductible excess. "
                f"Always consult network locations before filing a claim to avoid coverage reductions."
            )
            
            q1 = find_verbatim_quote(["depreciation", "percent"], "Depreciation rates of up to 50% shall apply on nylon, plastic, rubber parts and batteries replaced during vehicle repair claims.")
            q2 = find_verbatim_quote(["deductible", "excess"], "A compulsory deductible excess of INR 2,00,000 shall be borne by the insured for every separate claim event under this policy.")
            q3 = find_verbatim_quote(["network", "garage"], "Reimbursements for repairs undertaken at non-network garages are restricted to 70% of standard estimated surveyor repair costs.")

            hidden_traps = [
                {
                    "id": 1, "severity": "Critical", "title": "50% Depreciation on Parts",
                    "original_text": q1,
                    "plain_explanation": "For parts like bumpers or plastic components, you must pay 50% of the replacement cost yourself.",
                    "impact": "Saves the insurer money but costs you ₹10,000+ during an accident repair.",
                    "advice": "Opt for a Zero-Depreciation add-on cover by paying a small extra premium."
                },
                {
                    "id": 2, "severity": "High", "title": "Compulsory Deductible Excess",
                    "original_text": q2,
                    "plain_explanation": "For every single claim, you must pay the first ₹2,000 yourself before the insurer pays anything.",
                    "impact": "Minor repairs or scratches under ₹2,000 are not worth claiming since you pay the full amount anyway.",
                    "advice": "Avoid claiming for minor paint scuffs to protect your No Claim Bonus (NCB)."
                },
                {
                    "id": 3, "severity": "Medium", "title": "Non-Network Garage Limit",
                    "original_text": q3,
                    "plain_explanation": "If you get your vehicle repaired outside the insurer's network of garages, they will only reimburse 70% of standard rates.",
                    "impact": "You are exposed to significant out-of-pocket expenses if towed to a local independent garage.",
                    "advice": "Always check and confirm cashless network garage locations prior to scheduling repairs."
                }
            ]
            friendly_explanations = [
                { "legal_text": "Compulsory deductible excess clause.", "friendly_text": "You must pay the first pocket-sized chunk of any repair bill before insurance covers the rest.", "emoji": "🚗", "category": "Insurance" }
            ]
            verdict = "This comprehensive motor policy offers good third-party shielding but high parts depreciation and garage restrictions. A Zero-depreciation add-on is highly recommended."
            top_risk = "50% parts depreciation schedule on plastics/rubber."
            flag = "Composite parts depreciation deduction"
            flag_reason = "Applying high depreciation on wear parts substantially reduces insurer claims payout."
            flag_orig = q1

        elif insurance_sub_type == "Life Insurance":
            summary = (
                f"This premium term life policy from {lender_name} secures a death benefit payout of {loan_amount} for your designated nominees. "
                f"However, it contains a critical absolute disclosure warranty where any minor omission or history mismatch can fully void the policy. "
                f"Furthermore, self-harm and suicide exclusions strictly apply for the first 12 months, and early policy surrenders prior to year 3 incur steep 100% forfeitures. "
                f"Ensure absolute medical history accuracy when filling out proposal forms to protect your family's future."
            )
            
            q1 = find_verbatim_quote(["disclosure", "declare"], "Any material misrepresentation, omission, or non-declaration of pre-existing health habits will render this policy void ab initio.")
            q2 = find_verbatim_quote(["suicide", "exclude"], "No death benefit shall be payable if the life insured commits suicide, whether sane or insane, within 12 months of inception.")
            q3 = find_verbatim_quote(["surrender", "charge"], "Early surrender or policy termination prior to year 3 yields zero surrender value, and active surrender charges of up to 40% apply in year 4.")

            hidden_traps = [
                {
                    "id": 1, "severity": "Critical", "title": "Absolute Disclosure Warranty",
                    "original_text": q1,
                    "plain_explanation": "If you forget to list a minor medical habit or past checkup, the insurer can declare the policy void and refuse to pay your family when you die.",
                    "impact": "Nominees get a ₹0 payout after years of premium payments due to minor history discrepancies.",
                    "advice": "Fill out the proposal form yourself and declare every single medical checkup or history detail, no matter how minor."
                },
                {
                    "id": 2, "severity": "High", "title": "First-Year Suicide Exclusion",
                    "original_text": q2,
                    "plain_explanation": "If death occurs by suicide in the first 12 months, no death benefit is paid; only the premiums paid are returned.",
                    "impact": "Nominees are barred from claim settlements in the first year under specific self-harm circumstances.",
                    "advice": "Be aware of standard suicide exclusions which are standard industry practice across almost all insurers."
                },
                {
                    "id": 3, "severity": "Medium", "title": "Steep Surrender Charges",
                    "original_text": q3,
                    "plain_explanation": "If you stop paying premiums early or surrender the policy, you lose all your money or face massive exit penalties.",
                    "impact": "Cancelling in year 2 or 3 means your entire investment is completely forfeited.",
                    "advice": "Choose pure term plans over expensive endowment plans to keep premium costs highly flexible and low."
                }
            ]
            friendly_explanations = [
                { "legal_text": "Material misrepresentation voids contract.", "friendly_text": "If you leave out any medical info when signing, the insurer can cancel the policy and refuse to pay your family.", "emoji": "❤️", "category": "Insurance" }
            ]
            verdict = "This term life policy has a substantial death benefit but extremely strict disclosure criteria. Fill out forms yourself to guarantee complete accuracy."
            top_risk = "Material non-disclosure voidability clause."
            flag = "Surrender forfeiture charges"
            flag_reason = "Forfeiting 100% of accumulated premiums for early exits creates extreme customer locked-in loss."
            flag_orig = q3

        elif insurance_sub_type == "Property Insurance":
            summary = (
                f"This structural property policy from {lender_name} covers dwelling structure damages up to {loan_amount} against fire and basic hazards. "
                f"However, it mandates the lending bank as the primary beneficiary, meaning claim settlements go directly to clearing your outstanding mortgage balance rather than providing you with construction funds. "
                f"Additionally, it strictly excludes damage from earth shifts, subsidence, or landslides, and applies a compounding building-age depreciation factor. "
                f"Check with the bank to establish rebuilding escrows before finalizing."
            )
            
            q1 = find_verbatim_quote(["beneficiary", "bank"], "In the event of structural damage, all claim proceeds shall be paid directly to the lending bank named as primary beneficiary.")
            q2 = find_verbatim_quote(["subsidence", "landslide"], "Damage arising from structural subsidence, landslide, ground movement, or coastal erosion is strictly excluded.")
            q3 = find_verbatim_quote(["depreciation", "age"], "A structural depreciation factor of 2.5% per annum applies to the property structure value based on building age.")

            hidden_traps = [
                {
                    "id": 1, "severity": "Critical", "title": "Bank Named as Sole Beneficiary",
                    "original_text": q1,
                    "plain_explanation": "If your house is damaged, the insurance money goes directly to pay off your mortgage balance, not to you for rebuilding.",
                    "impact": "You are left with no home and no rebuilding funds, though your bank loan is cleared.",
                    "advice": "Request a clause ensuring that funds can be disbursed into a joint escrow for rebuilding purposes."
                },
                {
                    "id": 2, "severity": "High", "title": "Subsidence & Landslide Exclusion",
                    "original_text": q2,
                    "plain_explanation": "If your home collapses or gets damaged due to earth movement, landslide, or ground shifting, you aren't covered.",
                    "impact": "A mudslide or soft soil shift can completely ruin your property and leave you with ₹0 assistance.",
                    "advice": "Purchase an add-on rider covering earthquake, landslide, and geological shifts if in sensitive areas."
                },
                {
                    "id": 3, "severity": "Medium", "title": "Annual Structural Depreciation",
                    "original_text": q3,
                    "plain_explanation": "The insurer reduces the payout value of your building structure by 2.5% every year based on its age.",
                    "impact": "For a 10-year-old building, you will only receive 75% of the actual reconstruction cost.",
                    "advice": "Insist on a 'Reinstatement Value' policy where claims are paid based on reconstruction cost without depreciation."
                }
            ]
            friendly_explanations = [
                { "legal_text": "Lender named as primary loss payee.", "friendly_text": "If a disaster happens, the insurance check goes directly to your bank to settle the debt, not to your pocket.", "emoji": "🏠", "category": "Insurance" }
            ]
            verdict = "This property policy secures basic fire coverage but is heavily weighted towards protecting the lending bank rather than rebuilding the homeowner's life."
            top_risk = "Bank named as sole primary beneficiary."
            flag = "Earth shift subsidence exclusion clause"
            flag_reason = "Excluding basic earth movements is a standard trap that voids coverage in soft soil terrains."
            flag_orig = q2

        else: # Health Insurance (Default)
            summary = (
                f"This premium health insurance policy from {lender_name} establishes a Sum Insured of {loan_amount} for primary hospitalizations. "
                f"However, it contains a critical mandatory 20% co-payment clause on specialized treatments and a strict 1% room rent sub-limit that can lead to large proportional deduction fees. "
                f"Additionally, a long 36-month waiting period applies to chronic conditions like diabetes and hypertension before they are fully covered. "
                f"Review network hospitals and ward types carefully to minimize out-of-pocket exposure."
            )
            
            q1 = find_verbatim_quote(["co-payment", "share"], "The insured agrees to a mandatory co-payment ratio of 20% on all specialized surgery treatments and hospitalizations.")
            q2 = find_verbatim_quote(["room rent", "limit"], "Hospital room rent charges are capped at a strict sub-limit of 1% of the overall Sum Insured per day.")
            q3 = find_verbatim_quote(["waiting period", "chronic"], "A mandatory waiting period of 36 months applies to all claims related to diabetes, hypertension, and joint treatments.")

            hidden_traps = [
                {
                    "id": 1, "severity": "Critical", "title": "20% Mandatory Co-Payment",
                    "original_text": q1,
                    "plain_explanation": "For every medical bill, you are forced to pay 20% of the total cost out of your own savings.",
                    "impact": "On a ₹5,00,000 major surgery claim, you must pay ₹1,00,000 cash yourself.",
                    "advice": "Request an insurance upgrade to a '0% Co-Pay' plan by paying a minor premium addition."
                },
                {
                    "id": 2, "severity": "High", "title": "1% Room Rent Sub-Limit",
                    "original_text": q2,
                    "plain_explanation": "The maximum the insurer pays for your hospital room per day is capped. Nicer rooms incur huge personal costs.",
                    "impact": "If room costs ₹10,000/day but limit is ₹5,000, you pay ₹5,000/day plus a proportional reduction on all doctor fees.",
                    "advice": "Insist on an insurance plan with 'No Room Rent Caps' to avoid treatment deductions."
                },
                {
                    "id": 3, "severity": "Medium", "title": "36-Month Waiting Period",
                    "original_text": q3,
                    "plain_explanation": "You are barred from claiming any insurance benefits for chronic ailments during the first 3 years.",
                    "impact": "You must fund all treatments for diabetes, high blood pressure, or joint issues for 36 months.",
                    "advice": "Ask if you can pay an extra fee to reduce waiting periods to 12 months."
                }
            ]
            friendly_explanations = [
                { "legal_text": "Daily room rent capping limitations.", "friendly_text": "Insurer won't pay for premium luxury rooms during hospitalizations.", "emoji": "🏥", "category": "Insurance" }
            ]
            verdict = "This health policy covers massive sum insured limits but has severe room rent caps and co-pays. Perfect for basic hospitalization but expensive for premium ward rooms."
            top_risk = "Mandatory 20% co-payment rule on specialized surgeries."
            flag = "Proportional treatment deduction clause"
            flag_reason = "Tying all medical expenses to the room rent sub-limit allows the insurer to trim your claims."
            flag_orig = q2

    elif category == "Lease":
        summary = f"This residential lease from {lender_name} specifies a monthly rental rate of {loan_amount} with a {interest_rate}. However, it contains unilateral 7-day landlord evictions, automatic uncapped rent escalations, and highly aggressive security deposit wear-and-tear deductions."
        
        q1 = find_verbatim_quote(["terminate", "notice"], "The Landlord may terminate this lease agreement and demand immediate premises possession upon giving a 7-day written notice.")
        q2 = find_verbatim_quote(["deposit", "deduct"], "The security deposit shall be refunded after deducting uncapped fees for general maintenance, painting, and wear-and-tear.")
        q3 = find_verbatim_quote(["escalate", "rent"], "Upon lease renewal, the monthly rent shall automatically escalate by a flat rate of 12% without further market rate assessment.")

        hidden_traps = [
            {
                "id": 1, "severity": "Critical", "title": "7-Day Landlord Eviction Notice",
                "original_text": q1,
                "plain_explanation": "The landlord can force you to pack up and move out within a week with zero legal justification.",
                "impact": "Forces massive emergency relocation expenses, broker fees, and intense housing search pressure.",
                "advice": "Alter this clause to require at least a standard 30-day or 60-day notice for eviction."
            },
            {
                "id": 2, "severity": "High", "title": "Uncapped Wear-and-Tear Deductions",
                "original_text": q2,
                "plain_explanation": "The landlord can deduct any money they want from your security deposit for simple painting or cleaning.",
                "impact": "You could lose your entire ₹44,000 security deposit for normal scuffs or marks.",
                "advice": "Amend this clause to explicitly exclude 'normal wear-and-tear' from deposit deductions."
            },
            {
                "id": 3, "severity": "Medium", "title": "12% Automatic Rent Escalation",
                "original_text": q3,
                "plain_explanation": "Your rent goes up by a flat 12% next year, regardless of whether property prices fall.",
                "impact": "Your annual rent outlay increases by ₹31,680 next year.",
                "advice": "Negotiate to cap annual rental increases at 5% maximum."
            }
        ]
        friendly_explanations = [
            { "legal_text": "Deposit deduction for paint wear.", "friendly_text": "Landlord using tenant money to repaint standard scuffs.", "emoji": "🏠", "category": "Rights" }
        ]
        verdict = "The lease is standard but very tenant-unfavorable. The 7-day eviction notice and uncapped security deposit deductions represent significant financial and moving risks."
        top_risk = "Unilateral 7-day landlord termination notice."
        flag = "Wear-and-tear repaint charge"
        flag_reason = "Forcing tenants to pay for professional repainting is a standard landlord trap."
        flag_orig = q2

    else: # Loan
        summary = f"This Home Loan contract from {lender_name} provides {loan_amount} at {interest_rate}. However, it enforces uncapped floating benchmark resets, substantial penal compound interest rates on defaults, and uncapped exit prepayment charges."
        
        q1 = find_verbatim_quote(["margin", "sole discretion"], "The Lender reserves the absolute right to revise the benchmark rate spread from time to time at its sole discretion.")
        q2 = find_verbatim_quote(["penal", "default"], "Any default in payment of EMI will attract additional interest at 2% per month compounded on outstanding arrears.")
        q3 = find_verbatim_quote(["prepayment", "charge"], "Prepayment or transfer of the outstanding balance will attract a flat foreclosure charge of 2% of the principal sum.")

        hidden_traps = [
            {
                "id": 1, "severity": "Critical", "title": "Unilateral Floating Margin Revision",
                "original_text": q1,
                "plain_explanation": "The bank can raise your interest rate whenever they want, even if market rates do not change, without asking your permission.",
                "impact": "A 1% increase in interest rate will add over ₹7,0,000 of extra lifetime interest cost to your loan balance.",
                "advice": "Bargain to add a margin cap clause that restricts spread adjustments to a maximum of 1% annually."
            },
            {
                "id": 2, "severity": "High", "title": "2% Compounded Late Penal Interest",
                "original_text": q2,
                "plain_explanation": "If you are late on a payment, the bank charges you an extremely high penalty rate that compounds month after month.",
                "impact": "Missing just 2 payments can trigger cumulative penalties of over ₹12,000 within weeks.",
                "advice": "Ask the bank if they can offer a 15-day grace period before compound late penalties are applied."
            },
            {
                "id": 3, "severity": "Medium", "title": "2% Uncapped Prepayment Exit Penalties",
                "original_text": q3,
                "plain_explanation": "If you decide to prepay your loan early or transfer it to a cheaper bank, you have to pay a massive exit fee.",
                "impact": "Transferring the loan in year 5 will cost you over ₹90,000 upfront as exit fees.",
                "advice": "Negotiate to waive the foreclosure penalty after the third year of active repayment."
            }
        ]
        friendly_explanations = [
            { "legal_text": "Floating spread margin revision indexes.", "friendly_text": "The margin rate added to basic central bank interest index can be shifted by lender.", "emoji": "💸", "category": "Interest" }
        ]
        verdict = "This floating rate loan offers competitive starting rates but exposes you to severe margin risk and exit prepayment penalties if refinance is sought."
        top_risk = "Uncapped unilateral floating benchmark interest spread revisions."
        flag = "Penal compound interest rate"
        flag_reason = "Compounding late fees at 24% annually creates rapid debt traps."
        flag_orig = q2

    return json.dumps({
      "core_info": {
        "loan_type": category + (" Policy" if category in ["Pet", "Insurance"] else " Agreement"),
        "lender_name": lender_name,
        "borrower_name": borrower_name,
        "loan_amount": loan_amount,
        "loan_amount_numeric": loan_amount_numeric,
        "interest_rate": interest_rate,
        "interest_rate_numeric": interest_rate_numeric,
        "interest_type": interest_type,
        "tenure": tenure,
        "tenure_months": tenure_months,
        "emi_amount": emi_amount,
        "emi_numeric": emi_numeric,
        "processing_fee": processing_fee,
        "document_date": document_date,
        "summary": summary,
        "document_quality": "Clear"
      },
      "hidden_traps": hidden_traps,
      "friendly_explanations": friendly_explanations,
      "risk_score": {
        "overall_score": 60 if category == "Loan" else 65 if category == "Lease" else 55,
        "overall_level": "Medium Risk" if category != "Lease" else "High Risk",
        "overall_color": "amber" if category != "Lease" else "orange",
        "sub_scores": {
          "penalty_risk": 80, "interest_stability": 40, "transparency": 75, "fairness": 70, "legal_complexity": 50
        },
        "verdict": verdict,
        "top_risk_factor": top_risk
      },
      "suspicious_clauses": {
        "overall_suspicion": "Minor Concerns",
        "suspicious_items": [
          {
            "id": 1,
            "flag": flag,
            "confidence": 85,
            "reason": flag_reason,
            "original_text": flag_orig,
            "industry_standard": "All key rates, fees and penalties must be flat, transparent and capped.",
            "severity": "High Concern"
          }
        ]
      },
      "reality_cost": {
        "shock_statement": "The total amortized cost includes standard base premiums/fees.",
        "principal": loan_amount_numeric,
        "total_interest": interest_rate_numeric * tenure_months if type(interest_rate_numeric) in [int, float] else 0,
        "total_payment": loan_amount_numeric + (interest_rate_numeric * tenure_months if type(interest_rate_numeric) in [int, float] else 0),
        "interest_percentage": 8.5,
        "yearly_breakdown": [
          {
            "year": 1,
            "emi_paid": emi_numeric * 12 if type(emi_numeric) in [int, float] else 0,
            "interest_paid": interest_rate_numeric * 12 if type(interest_rate_numeric) in [int, float] else 0,
            "principal_paid": loan_amount_numeric // max(1, (tenure_months // 12)),
            "remaining_balance": max(0, loan_amount_numeric - (loan_amount_numeric // max(1, (tenure_months // 12))))
          }
        ]
      },
      "trust_score": {
        "transparency_score": 75, "transparency_note": "Core cost items are stated but dynamic penalty margins are vague.",
        "fairness_score": 60, "fairness_note": "Unilateral adjustment privileges heavily favor the lender's interest margins.",
        "complexity_score": 45, "complexity_note": "Standard legal phrasing requires active review.",
        "trust_grade": "B", "trust_grade_label": "Fairly Trustworthy",
        "trust_summary": "The document utilizes industry standard boilerplate language but includes multiple unfavorable clauses."
      }
    })

