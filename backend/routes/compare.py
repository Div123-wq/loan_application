import json
from flask import Blueprint, request, jsonify
from routes.upload import get_document_text, document_store
from services.analysis_service import perform_master_analysis
from services.github_ai_service import chat_json

compare_bp = Blueprint('compare', __name__)

COMPARE_SYSTEM = """You are LoanLens AI — a neutral loan comparison expert.
You objectively compare multiple loan documents to find the best option for the borrower.
Always return structured, specific JSON comparisons."""


@compare_bp.route('/api/compare', methods=['POST'])
def compare_loans():
    """Feature 6: Loan Comparison Battle — compare 2-3 loan documents."""
    data = request.get_json()
    doc_ids = data.get('doc_ids', [])

    if len(doc_ids) < 2:
        return jsonify({"error": "At least 2 document IDs required for comparison."}), 400
    if len(doc_ids) > 3:
        return jsonify({"error": "Maximum 3 documents can be compared at once."}), 400

    loan_summaries = []
    for i, doc_id in enumerate(doc_ids):
        try:
            text = get_document_text(doc_id)
            master_data = perform_master_analysis(text)
            core = master_data.get("core_info", {})
            traps = master_data.get("hidden_traps", [])
            risk = master_data.get("risk_score", {})
            reality_cost_principal = core.get("loan_amount_numeric")
            reality_cost_rate = core.get("interest_rate_numeric")
            reality_cost_months = core.get("tenure_months")
            
            try:
                reality_cost_principal = float(reality_cost_principal) if reality_cost_principal is not None else 500000
                reality_cost_rate = float(reality_cost_rate) if reality_cost_rate is not None else 12.0
                reality_cost_months = int(reality_cost_months) if reality_cost_months is not None else 60
            except (TypeError, ValueError):
                reality_cost_principal = 500000
                reality_cost_rate = 12.0
                reality_cost_months = 60
                
            monthly_rate = reality_cost_rate / 12 / 100
            emi = 0
            if monthly_rate > 0:
                emi = reality_cost_principal * monthly_rate * (1 + monthly_rate) ** reality_cost_months / ((1 + monthly_rate) ** reality_cost_months - 1)
            total_payment = emi * reality_cost_months

            loan_summaries.append({
                "index": i + 1,
                "doc_id": doc_id,
                "filename": document_store.get(doc_id, {}).get("filename", f"Loan {i+1}"),
                "loan_type": core.get("loan_type", "Unknown"),
                "lender": core.get("lender_name", "Unknown"),
                "amount": core.get("loan_amount", "N/A"),
                "amount_numeric": reality_cost_principal,
                "rate": core.get("interest_rate", "N/A"),
                "rate_numeric": reality_cost_rate,
                "tenure": core.get("tenure", "N/A"),
                "tenure_months": reality_cost_months,
                "interest_type": core.get("interest_type", "N/A"),
                "emi": f"₹{emi:,.0f}",
                "emi_numeric": round(emi, 0),
                "total_payment": f"₹{total_payment:,.0f}",
                "total_payment_numeric": round(total_payment, 0),
                "risk_score": risk.get("overall_score", 50),
                "risk_level": risk.get("overall_level", "Medium Risk"),
                "trap_count": len(traps),
                "critical_traps": sum(1 for t in traps if t.get("severity") == "Critical"),
            })
        except Exception as e:
            return jsonify({"error": f"Failed to analyze doc {doc_id}: {str(e)}"}), 500

    # AI comparative analysis
    summaries_text = json.dumps(loan_summaries, indent=2)
    prompt = f"""Compare these loan options and give an expert verdict.

LOAN DATA:
{summaries_text}

Return JSON:
{{
  "winner_cheapest": {{
    "doc_id": "id here",
    "reason": "Why this is cheapest"
  }},
  "winner_safest": {{
    "doc_id": "id here",
    "reason": "Why this is safest"
  }},
  "winner_overall": {{
    "doc_id": "id here",
    "reason": "Best overall recommendation"
  }},
  "comparison_table": [
    {{
      "category": "Total Cost",
      "winner": "Loan 1",
      "insight": "₹50,000 cheaper"
    }},
    {{
      "category": "Risk Level",
      "winner": "Loan 2",
      "insight": "Fewer hidden traps"
    }},
    {{
      "category": "Interest Rate",
      "winner": "Loan 1",
      "insight": "0.5% lower rate saves significantly"
    }},
    {{
      "category": "Flexibility",
      "winner": "Loan 2",
      "insight": "Better prepayment terms"
    }}
  ],
  "radar_scores": {{
    "labels": ["Cost", "Risk", "Transparency", "Flexibility", "Terms"],
    "datasets": []
  }},
  "negotiation_tips": [
    "Ask Loan 1 lender to match Loan 2's processing fee",
    "Request removal of prepayment penalty"
  ],
  "final_verdict": "3-4 sentence expert recommendation"
}}"""

    result = chat_json(COMPARE_SYSTEM, prompt)
    comparison = json.loads(result)

    return jsonify({
        "success": True,
        "loans": loan_summaries,
        "comparison": comparison
    })
