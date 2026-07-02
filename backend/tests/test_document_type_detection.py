import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.analysis_service import perform_master_analysis
from services.github_ai_service import chat, get_mock_chat_response, get_mock_json_response


def test_insurance_document_is_not_rendered_as_loan():
    insurance_text = """
    Star Health Insurance Company
    Health Insurance Policy
    Policyholder: Rohan Sharma
    Sum Insured: ₹5,00,000
    Annual Premium: ₹8,500
    Waiting Period: 24 months
    Exclusions: Pre-existing diseases
    """

    result = perform_master_analysis(insurance_text)
    core_info = result.get("core_info", {})

    assert "insurance" in str(core_info.get("loan_type", "")).lower()
    assert core_info.get("loan_amount_numeric") == 500000
    assert core_info.get("emi_numeric") == 708


def test_mock_chat_and_summary_use_insurance_context():
    insurance_text = """
    Star Health Insurance Company
    Health Insurance Policy
    Sum Insured: ₹5,00,000
    Annual Premium: ₹8,500
    Waiting Period: 24 months
    Co-payment: 20%
    """

    chat_response = get_mock_chat_response(f"LOAN DOCUMENT CONTEXT:\n{insurance_text}")
    assert "sum insured" in chat_response.lower() or "premium" in chat_response.lower()
    assert "waiting period" in chat_response.lower() or "co-pay" in chat_response.lower()

    json_response = get_mock_json_response(f"DOCUMENT TEXT:\n{insurance_text}")
    data = json.loads(json_response)
    summary = data["core_info"]["summary"].lower()
    assert "sum insured" in summary or "waiting period" in summary or "co-payment" in summary


def test_chat_fallback_uses_system_prompt_context():
    system_prompt = "LOAN DOCUMENT CONTEXT:\nHealth Insurance Policy\nSum Insured: ₹5,00,000\nAnnual Premium: ₹8,500\nWaiting Period: 24 months\nCo-payment: 20%"

    response = chat(system_prompt, "What are the biggest risks in this document?")

    response_lower = response.lower()
    assert "waiting period" in response_lower or "co-payment" in response_lower or "premium" in response_lower


def test_greeting_message_does_not_trigger_risk_fallback():
    system_prompt = "LOAN DOCUMENT CONTEXT:\nHealth Insurance Policy\nSum Insured: ₹5,00,000\nAnnual Premium: ₹8,500\nWaiting Period: 24 months\nCo-payment: 20%"

    response = chat(system_prompt, "User: What are the biggest risks in this document?\nAssistant: Yes, this policy has a few important risk points.\n\nUser: hi")

    response_lower = response.lower()
    assert "hello" in response_lower or "hi" in response_lower or "help" in response_lower


def test_coverage_and_processing_charge_questions_get_specific_answers():
    system_prompt = "LOAN DOCUMENT CONTEXT:\nHealth Insurance Policy\nSum Insured: ₹5,00,000\nAnnual Premium: ₹8,500\nWaiting Period: 24 months\nCo-payment: 20%\nProcessing Fee: ₹1,000 Administration Fee"

    coverage_response = chat(system_prompt, "User: tell me about coverage")
    charges_response = chat(system_prompt, "User: what will be the processing charges")

    assert "sum insured" in coverage_response.lower() or "waiting period" in coverage_response.lower()
    assert "₹1,000" in charges_response or "processing fee" in charges_response.lower() or "administration fee" in charges_response.lower()
