import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')
from services.github_ai_service import get_mock_json_response

TESTS = {
    "Health Insurance (X,XX,XXX INR format)": """Health Insurance Policy
Insurer: StarCare Health Insurance
Policyholder: Amit Kumar
Sum Insured: 5,00,000 INR
Premium: 8,500 INR per year
Co-payment: 20% on all claims
Room rent limit: 1% of sum insured per day""",

    "Auto Insurance (Rs. prefix format)": """Motor Vehicle Insurance Certificate
Insurer: Bajaj Allianz General Insurance
Policyholder Name: Priya Mehta
Coverage: Rs. 8,00,000
Annual Premium: Rs. 12,000
Vehicle: Honda City
Depreciation on plastic parts: 50%""",

    "Life Insurance (INR suffix large)": """Term Life Policy
Insurance Company: LIC of India
Life Insured: Ramesh Kumar
Sum Assured: 50,00,000 INR
Annual Premium: 25,000 INR
Nominee: Sunita Kumar""",

    "Home Loan (standard)": """Home Loan Agreement
Bank: HDFC Bank
Borrower: Suresh Patel
Principal Amount: 35,00,000 INR
Interest Rate: 9.2%
EMI: 31,500 INR per month""",
}

ok = True
for name, doc in TESTS.items():
    prompt = f"DOCUMENT TEXT:\n{doc}\n\nYou must return a single JSON object"
    res = json.loads(get_mock_json_response(prompt))
    ci = res["core_info"]
    print(f"=== {name} ===")
    print(f"  type    : {ci['loan_type']}")
    print(f"  lender  : {ci['lender_name']}")
    print(f"  borrower: {ci['borrower_name']}")
    print(f"  amount  : {ci['loan_amount']}")
    print(f"  rate    : {ci['interest_rate']}")
    print(f"  traps   : {[t['title'] for t in res['hidden_traps']]}")

    # Basic assertions
    if "Insurance" in name:
        assert "insurance" in ci["loan_type"].lower(), f"FAIL: Expected Insurance type, got {ci['loan_type']}"
        assert ci["loan_amount"] not in ("", None), f"FAIL: loan_amount is blank for {name}"
    elif "Loan" in name:
        assert "loan" in ci["loan_type"].lower() or "agreement" in ci["loan_type"].lower(), \
            f"FAIL: Expected Loan type, got {ci['loan_type']}"
    print("  PASS")
    print()

print("All tests passed!" if ok else "Some tests failed.")
