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
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt + "\n\nRespond ONLY with valid JSON."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
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
    """Fallback standard mock JSON for structured endpoints."""
    p_lower = prompt.lower()
    
    # Comparison Battle
    if "compare" in p_lower or "winner_cheapest" in p_lower or "winner" in p_lower:
        return json.dumps({
          "winner_cheapest": {
            "doc_id": "mock_id_1",
            "reason": "The primary agreement offers significantly lower upfront administrative levies and dynamic MCLR resets, making it the cheapest over a 5-year outlook."
          },
          "winner_safest": {
            "doc_id": "mock_id_2",
            "reason": "The comparison offer features flat, transparent interest structures without uncapped foreclosure penalty clauses, ensuring safety."
          },
          "winner_overall": {
            "doc_id": "mock_id_1",
            "reason": "The primary agreement presents the best balance of lower initial EMI rates and lenient terms, provided seasonal prepayments are utilized."
          },
          "comparison_table": [
            {
              "category": "Total Cost",
              "winner": "SBI Home Loan",
              "insight": "₹50,000 cheaper overall"
            },
            {
              "category": "Risk Level",
              "winner": "SBI Home Loan",
              "insight": "Fewer critical hidden traps (3 traps vs 5 traps in HDFC)"
            },
            {
              "category": "Interest Rate",
              "winner": "HDFC Fixed Buffer",
              "insight": "0.25% lower starting rate shields initial years"
            },
            {
              "category": "Flexibility",
              "winner": "SBI Home Loan",
              "insight": "No foreclosure charges after Year 3"
            }
          ],
          "radar_scores": {
            "labels": ["Cost", "Risk", "Transparency", "Flexibility", "Terms"],
            "datasets": [
              {
                "label": "SBI Home Loan",
                "data": [85, 80, 75, 90, 80]
              },
              {
                "label": "HDFC Home Loan",
                "data": [80, 60, 70, 50, 70]
              }
            ]
          },
          "negotiation_tips": [
            "Request the primary lender to match the competitor's 8.25% starting interest rates for the initial year.",
            "Ask the competing lender to completely waive the 2% exit foreclosure penalty after Year 3."
          ],
          "final_verdict": "While the competitor is slightly cheaper initially, their high prepayment penalty of 2% is a hidden trap if you plan to refinance. The primary option stands out as the overall safer long-term choice."
        })

    # Negotiation structure
    if "negotiate" in p_lower or "negotiable_terms" in p_lower:
        return json.dumps({
          "negotiable_terms": [
            {
              "term": "Flat Administrative Levy",
              "current": "INR 15,000",
              "negotiable_to": "INR 0",
              "success_probability": "High",
              "how_to_ask": "Request a waiver as a high-credit borrower who is already paying standard upfront processing fees."
            },
            {
              "term": "Foreclosure Penalty Exit Fee",
              "current": "2% of principal outstanding",
              "negotiable_to": "0% penalty after Year 3",
              "success_probability": "Medium",
              "how_to_ask": "Mention competitor banks do not charge exit penalties for loans foreclosed using your own savings."
            }
          ],
          "questions_for_bank": [
            "Is the foreclosure penalty waivable after 3 years?",
            "Can we cap the floating interest rate margin adjustment?"
          ],
          "best_time_to_negotiate": "Before signing — never after",
          "leverage_points": [
            "Your solid credit rating of 780 gives you strong leverage."
          ],
          "red_lines": [
            "Do NOT accept variable rate without a margin cap clause."
          ],
          "negotiation_script": "I would love to move forward, but the 2% exit foreclosure penalty and INR 15,000 administrative charge deviate from standard offerings. Could we waive the exit fee after year 3?"
        })

    # Pressure / Cash Flow Stress Calculator
    if "pressure" in p_lower or "stress_level" in p_lower:
        salary = 120000.0
        expenses = 45000.0
        family_size = 3
        obligations = "School fees in June, Rent"
        
        import re
        sal_match = re.search(r"Monthly Salary: ₹([\d,]+)", prompt)
        if sal_match:
            salary = float(sal_match.group(1).replace(",", ""))
            
        exp_match = re.search(r"Monthly Expenses: ₹([\d,]+)", prompt)
        if exp_match:
            expenses = float(exp_match.group(1).replace(",", ""))
            
        fam_match = re.search(r"Family Size: (\d+)", prompt)
        if fam_match:
            family_size = int(fam_match.group(1))

        ob_match = re.search(r"Other Obligations: (.*)", prompt)
        if ob_match:
            obligations = ob_match.group(1).strip()
            
        monthly_surplus = salary - expenses
        emi_to_income_ratio = round((21700.0 / salary * 100.0), 1) if salary > 0 else 30.0
        
        # Calculate dynamic stress index
        net_margin = salary - expenses - 21700.0
        if net_margin < 0:
            stress_score = min(98, 70 + int(abs(net_margin) / 1000.0) * 3)
        else:
            stress_score = max(10, 70 - int(net_margin / 2000.0) * 2)
            
        stress_score += family_size * 4
        stress_score = min(max(stress_score, 12), 99)
        
        if stress_score >= 80:
            stress_level = "Critical Risk"
        elif stress_score >= 60:
            stress_level = "High Risk"
        elif stress_score >= 40:
            stress_level = "Medium Risk"
        else:
            stress_level = "Low Risk"
            
        # Detect obligated months
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        highlighted_months = []
        for m in months_list:
            if m.lower() in obligations.lower():
                highlighted_months.append(m)
                
        # Populate dynamic calendar
        monthly_calendar = []
        danger_months = []
        safe_months = []
        for m in months_list:
            m_lower = m.lower()
            m_stress = "Low"
            m_note = "Normal spending"
            
            is_obligated = m in highlighted_months
            
            if is_obligated:
                m_stress = "High"
                m_note = f"Obligation trigger: {obligations}"
                danger_months.append(m)
            elif m_lower == "march":
                m_stress = "High" if stress_score > 50 else "Medium"
                m_note = "Tax filing season"
                if m_stress == "High":
                    danger_months.append(m)
            elif m_lower == "october":
                m_stress = "High" if stress_score > 40 else "Medium"
                m_note = "Festival preps & Diwali outlay"
                if m_stress == "High":
                    danger_months.append(m)
            elif m_lower in ["may", "december"]:
                m_stress = "Medium"
                m_note = "Summer travel / Holiday season"
            else:
                if stress_score > 75:
                    m_stress = "Medium"
                    m_note = "Tight baseline surplus flow"
                else:
                    m_stress = "Low"
                    m_note = "Normal spending"
                    safe_months.append(m)
                    
            monthly_calendar.append({
                "month": m,
                "stress": m_stress,
                "note": m_note
            })
                    
        verdict = f"Your cash flow shows a surplus of ₹{monthly_surplus:,.0f} before EMI deductions. The dynamic debt commitment leads to a {stress_level.lower()} rating, meaning cash stress spikes seasonally during obligation periods."
        
        return json.dumps({
          "monthly_surplus": monthly_surplus,
          "emi_to_income_ratio": emi_to_income_ratio,
          "stress_level": stress_level,
          "stress_score": stress_score,
          "monthly_calendar": monthly_calendar,
          "danger_months": danger_months,
          "safe_months": safe_months,
          "lifestyle_impact": f"You should budget standard reserves to handle peak stress points. We advise trimming optional layout by {int(stress_score/3)}%.",
          "breaking_point_months": max(2, int(monthly_surplus / 5000.0)) if monthly_surplus > 0 else 0,
          "breaking_point_note": f"Without external backups, your cash pool supports about {max(2, int(monthly_surplus / 5000.0)) if monthly_surplus > 0 else 0} months of continuous stress before depleting.",
          "recommendations": [
            f"Establish standard dynamic reserves before seasonal payouts.",
            "Renegotiate variable rate options to restrict sudden hikes."
          ],
          "verdict": verdict
        })

    # What-If Simulator
    if "simulate" in p_lower or "timeline_effects" in p_lower:
        scenario = "What if I miss payments?"
        import re
        scen_match = re.search(r'borrower is asking: "(.*?)"', prompt)
        if scen_match:
            scenario = scen_match.group(1)
            
        s_lower = scenario.lower()
        
        if "miss" in s_lower or "late" in s_lower or "default" in s_lower or "delay" in s_lower:
            penalty_amount = "₹4,340 (2% penal compound interest)"
            extra_interest = "₹3,500"
            total_extra_cost = "₹7,840"
            credit_score_impact = "-50 to -80 points"
            total_extra_payment = "₹15,000 over tenure"
            recovery_timeline = "6-12 months"
            bank_action_risk = "High"
            severity_level = "High"
            timeline_effects = [
              {"month": 1, "event": "Late compound penalties applied", "cost": "₹4,340", "severity": "medium"},
              {"month": 2, "event": "Arrears reported to credit bureaus", "cost": "₹0", "severity": "high"},
              {"month": 3, "event": "Legal show-cause alert drafted", "cost": "₹15,000", "severity": "critical"}
            ]
            advice = [
              "Request a payment grace period from your banking relationship manager.",
              "Prepare a ₹20,000 buffer reserve to cover late compounded interests."
            ]
            plain_summary = "Missing your EMI payments triggers immediate penal compounding interests. Your credit score will experience substantial downgrades and bureaus are updated instantly."
            
        elif "prepay" in s_lower or "foreclose" in s_lower or "early" in s_lower or "close" in s_lower:
            penalty_amount = "₹1,00,000 exit penalty (2% principal outstanding)"
            extra_interest = "-₹12,45,000 interest saved!"
            total_extra_cost = "₹1,00,000"
            credit_score_impact = "+15 to +30 points (Clear of debt)"
            total_extra_payment = "₹1,00,000 exit penalty"
            recovery_timeline = "Immediate closure"
            bank_action_risk = "Low"
            severity_level = "Medium"
            timeline_effects = [
              {"month": 1, "event": "Foreclosure exit request submitted at bank branch", "cost": "₹1,00,000", "severity": "low"},
              {"month": 2, "event": "Savings liquidation check cleared", "cost": "₹0", "severity": "medium"},
              {"month": 3, "event": "Account closed & No Due Certificate (NOC) distributed", "cost": "₹0", "severity": "low"}
            ]
            advice = [
              "Formally request the branch manager to waive the prepayment penalty fee.",
              "Obtain a certified stamp signature on your original loan document NOC document."
            ]
            plain_summary = "Prepaying your loan saves massive cumulative interest payouts, though standard bank contracts levy a flat 2% exit foreclosure penalty on outstanding principal balances."
            
        elif "rate" in s_lower or "floating" in s_lower or "rise" in s_lower or "jump" in s_lower or "increase" in s_lower:
            penalty_amount = "₹0"
            extra_interest = "₹8,24,000 dynamic increase"
            total_extra_cost = "₹8,24,000"
            credit_score_impact = "0 points"
            total_extra_payment = "₹4,500 extra per EMI"
            recovery_timeline = "Duration of loan tenure"
            bank_action_risk = "Medium"
            severity_level = "High"
            timeline_effects = [
              {"month": 1, "event": "Dynamic MCLR rate index adjusted upwards by bank", "cost": "₹0", "severity": "medium"},
              {"month": 2, "event": "Monthly EMI payment draft revised upwards", "cost": "₹4,500", "severity": "medium"},
              {"month": 3, "event": "Total loan tenure dynamically extended by 18 months", "cost": "₹8,24,000", "severity": "high"}
            ]
            advice = [
              "Increase your monthly payment instead of lengthening tenure to minimize lifetime interest costs.",
              "Track your bank's reset cycle date closely to secure benchmark transparency."
            ]
            plain_summary = "Floating interest rate increases do not invoke penalties but directly increase total lifetime interest obligations or adjust monthly EMI draft requirements."
            
        else:
            # Customized dynamic fallback for any other typed text!
            penalty_amount = "₹2,500 standard administrative levy"
            extra_interest = "₹1,500"
            total_extra_cost = "₹4,000"
            credit_score_impact = "-10 to -30 points"
            total_extra_payment = "₹4,000"
            recovery_timeline = "3-6 months"
            bank_action_risk = "Medium"
            severity_level = "Medium"
            timeline_effects = [
              {"month": 1, "event": f"Scenario adjustment '{scenario}' reviewed", "cost": "₹2,500", "severity": "low"},
              {"month": 2, "event": "Bank technical fee processed", "cost": "₹1,500", "severity": "medium"},
              {"month": 3, "event": "Loan ledger amortizations revised", "cost": "₹0", "severity": "low"}
            ]
            advice = [
              f"Reach out to your banking branch relative to scenario '{scenario}'.",
              "Maintain dynamic backup liquidity options to safeguard cash flows."
            ]
            plain_summary = f"Your scenario '{scenario}' triggers general administrative bank guidelines. We recommend auditing the precise term shifts prior to execution."
            
        return json.dumps({
          "scenario": scenario,
          "immediate_impact": {
            "penalty_amount": penalty_amount,
            "extra_interest": extra_interest,
            "total_extra_cost": total_extra_cost
          },
          "timeline_effects": timeline_effects,
          "credit_score_impact": credit_score_impact,
          "total_extra_payment": total_extra_payment,
          "recovery_timeline": recovery_timeline,
          "bank_action_risk": bank_action_risk,
          "advice": advice,
          "severity_level": severity_level,
          "plain_summary": plain_summary
        })

    # Deadline Panic Predictor
    if "deadline" in p_lower or "upcoming_milestones" in p_lower:
        start_date = "2026-05-18"
        salary = 120000.0
        
        import re
        date_match = re.search(r"LOAN START DATE: ([\d-]+)", prompt)
        if date_match:
            start_date = date_match.group(1).strip()
            
        sal_match = re.search(r"MONTHLY SALARY: ₹([\d,]+)", prompt)
        if sal_match:
            salary = float(sal_match.group(1).replace(",", ""))
            
        # Parse year, month, day to build milestones dynamically
        try:
            year, month, day = map(int, start_date.split("-"))
            m1_date = f"{year+1}-{month:02d}-{day:02d}"
            m2_date = f"{year+2}-{month:02d}-{day:02d}"
            panic_month = "June"
            panic_period = f"{panic_month} {year+1}"
            prep_month = "March"
            prep_period = f"{prep_month} {year+1}"
        except Exception:
            m1_date = "2027-05-18"
            m2_date = "2028-05-18"
            panic_period = "June 2027"
            prep_period = "March 2027"
            
        # Dynamic calculations based on salary
        estimated_shortfall = "₹15,000" if salary > 80000 else "₹30,000 (Critical cash drain!)"
        risk_level = "High" if salary > 80000 else "Critical"
        save_amount = "₹5,000" if salary > 80000 else "₹10,000"
        
        return json.dumps({
          "upcoming_milestones": [
            {
              "date": m1_date,
              "event": "Year 1 Amortization Anniversary",
              "type": "milestone",
              "financial_note": f"₹5.2L principal amortized. Interest rate lock conversion triggers next month."
            },
            {
              "date": m2_date,
              "event": "Year 2 Principal Reduction Milestone",
              "type": "milestone",
              "financial_note": "₹11.4L paid. Equity release option unlocked at 8.25% MCLR."
            }
          ],
          "panic_periods": [
            {
              "period": panic_period,
              "reason": "School admission fees coincide with standard quarterly rate spread reviews, creating pressure spikes.",
              "risk_level": risk_level,
              "estimated_shortfall": estimated_shortfall,
              "advice": f"Shield your cash reserves: Set aside an extra {save_amount} per month beginning {prep_period} to comfortably absorb school fee obligations."
            }
          ],
          "5_year_forecast": {
            "easy_years": [1, 2],
            "challenging_years": [3, 5],
            "reason": f"MCLR floating spreads reset in Year 3. Borrowers earning ₹{salary:,.0f} per month will outpace EMI obligations fully by Year 5 as salary grows."
          },
          "smart_tip": f"Save up to 3x of your monthly EMI as a ring-fenced reserve. At ₹{salary:,.0f}/mo, an emergency liquid pool of ₹1.5L shields you from benchmark adjustments."
        })

    # Return standard high-fidelity consolidated master audit fallback
    return json.dumps({
      "core_info": {
        "loan_type": "Home Loan",
        "lender_name": "State Bank of India (MCLR Dynamic)",
        "borrower_name": "Rohan Sharma",
        "loan_amount": "₹50,00,000",
        "loan_amount_numeric": 5000000,
        "interest_rate": "8.5% p.a.",
        "interest_rate_numeric": 8.5,
        "interest_type": "Floating",
        "tenure": "20 Years",
        "tenure_months": 240,
        "emi_amount": "₹43,391",
        "emi_numeric": 43391,
        "processing_fee": "₹15,000 flat administrative levy",
        "document_date": "18 May 2026",
        "summary": "This is a premium-grade high-fidelity SBI home loan contract. While principal levels and starting rate ratios are standard, the contract includes aggressive MCLR floating margin definitions and substantial late compounding penalties.",
        "document_quality": "Clear"
      },
      "hidden_traps": [
        {
          "id": 1,
          "title": "Unilateral Floating Margin Clause",
          "severity": "High",
          "original_text": "The bank reserves the absolute right to revise the benchmark rate spread from time to time at its sole discretion.",
          "plain_explanation": "The bank can raise your interest rate whenever they want, even if market rates do not change, without asking your permission.",
          "impact": "A 1% increase in interest rate will add over ₹7,0,000 of extra lifetime interest cost to your loan balance.",
          "advice": "Bargain to add a margin cap clause that restricts spread adjustments to a maximum of 1% annually."
        },
        {
          "id": 2,
          "title": "Compounded Penal Interest Rates",
          "severity": "Critical",
          "original_text": "Any default in payment of EMI will attract additional interest at 2% per month compounded on outstanding arrears.",
          "plain_explanation": "If you are late on a payment, the bank charges you an extremely high penalty rate that compounds month after month.",
          "impact": "Missing just 2 payments can trigger cumulative penalties of over ₹12,000 within weeks.",
          "advice": "Ask the bank if they can offer a 15-day grace period before compound late penalties are applied."
        },
        {
          "id": 3,
          "title": "Uncapped Foreclosure exit levies",
          "severity": "High",
          "original_text": "Prepayment or transfer of the outstanding balance will attract a flat foreclosure charge of 2% of the principal sum.",
          "plain_explanation": "If you decide to prepay your loan early or transfer it to a cheaper bank, you have to pay a massive exit fee.",
          "impact": "Transferring the loan in year 5 will cost you over ₹90,000 upfront as exit fees.",
          "advice": "Negotiate to waive the foreclosure penalty after the third year of active repayment."
        }
      ],
      "friendly_explanations": [
        {
          "legal_text": "The borrower shall pay to the bank all charges for administrative tasks and technical evaluations.",
          "friendly_text": "You are paying for all the bank's internal reviews, even if the loan is rejected.",
          "emoji": "💸",
          "category": "Penalty"
        },
        {
          "legal_text": "The premium dynamic benchmark rate shall fluctuate in accordance with public policy MCLR adjustments.",
          "friendly_text": "Your rate changes when India's central bank adjusts core policy lending metrics.",
          "emoji": "📈",
          "category": "Interest"
        }
      ],
      "risk_score": {
        "overall_score": 60,
        "overall_level": "Medium Risk",
        "overall_color": "amber",
        "sub_scores": {
          "penalty_risk": 80,
          "interest_stability": 40,
          "transparency": 75,
          "fairness": 70,
          "legal_complexity": 50
        },
        "verdict": "This loan represents standard Indian floating rate risks. The initial rate is highly competitive, but the aggressive late compounds and exit fees place high pressure on long-term cash flows.",
        "top_risk_factor": "Unilateral spread adjustment reserves that let the bank change terms without consent."
      },
      "suspicious_clauses": {
        "overall_suspicion": "Minor Concerns",
        "suspicious_items": [
          {
            "id": 1,
            "flag": "Vague Administrative Fee Clauses",
            "confidence": 85,
            "reason": "Fees should be flat and specified; vague language allows the bank to add hidden charges later.",
            "original_text": "Other dynamic levies may be applied by the bank for seasonal audits.",
            "industry_standard": "All applicable fees must be clearly detailed in the core schedule.",
            "severity": "Unusual"
          }
        ]
      },
      "trust_score": {
        "transparency_score": 75,
        "transparency_note": "Core repayment parameters are clear, but hidden administrative levy details are vague.",
        "fairness_score": 60,
        "fairness_note": "Foreclosure fees and compound penalties heavily favor the lender's interest margins.",
        "complexity_score": 45,
        "complexity_note": "Written in standard legal English, requiring active financial knowledge to decipher completely.",
        "trust_grade": "B",
        "trust_grade_label": "Fairly Trustworthy",
        "trust_summary": "The document is standard for Tier-1 public sector banks but enforces several aggressive clauses that are highly unfavorable to individual retail borrowers."
      }
    })

