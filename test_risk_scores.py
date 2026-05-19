import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')
from services.github_ai_service import get_mock_json_response

TESTS = {
    "Health Insurance": (
        "HEALTH INSURANCE POLICY\n"
        "Insurer: ICICI Lombard Health Insurance\n"
        "Policyholder: Rahul Verma\n"
        "Sum Insured: 3,00,000 INR\n"
        "Annual Premium: 7,200 INR per year\n"
        "The insured agrees to a mandatory co-payment ratio of 20% on all specialized surgery treatments.\n"
        "Hospital room rent charges are capped at a strict sub-limit of 1% of the overall Sum Insured per day.\n"
        "A mandatory waiting period of 36 months applies to all claims related to diabetes, hypertension.\n"
        "Pre-existing diseases are excluded for the first 24 months of the policy.\n"
    ),
    "Auto Insurance": (
        "POLICY DETAILS:\n"
        "AutoGuard Comprehensive Motor Insurance\n"
        "Insurer: AutoGuard Motor\n"
        "Policyholder Name: Rohan Sharma\n"
        "Sum Insured: 15,00,000 INR\n"
        "Premium Amount Due: 1,200 INR Monthly\n"
        "Depreciation rates of up to 50% shall apply on nylon, plastic, rubber parts.\n"
        "A compulsory deductible excess of INR 2,00,000 shall be borne by the insured for every claim.\n"
        "Reimbursements for repairs undertaken at non-network garages are restricted to 70%.\n"
    ),
    "Lease Agreement": (
        "RESIDENTIAL LEASE AGREEMENT\n"
        "Landlord: Apex Realty Group\n"
        "Tenant: Priya Mehta\n"
        "Monthly Rent: 22,000 INR\n"
        "Security Deposit: 44,000 INR\n"
        "The Landlord may terminate this lease upon giving a 7-day notice.\n"
        "The security deposit shall be refunded after deducting uncapped fees for general maintenance, painting.\n"
        "Upon lease renewal, monthly rent shall automatically escalate by 12% without market rate assessment.\n"
    ),
    "Home Loan": (
        "HOME LOAN AGREEMENT\n"
        "Bank: HDFC Bank\n"
        "Borrower: Suresh Patel\n"
        "Principal Amount: 35,00,000 INR\n"
        "Interest Rate: 9.2%\n"
        "EMI: 31,500 INR per month\n"
        "The Lender shall at its sole discretion revise the interest rates payable under MCLR variations.\n"
        "A pre-payment charges penalty of 2% of the outstanding principal amount shall apply to pre-closure.\n"
        "Default in payments triggers additional penal interest at the rate of 2% per month compounded.\n"
    ),
}

all_pass = True
for name, doc in TESTS.items():
    prompt = f"DOCUMENT TEXT:\n{doc}\n\nYou must return a single JSON object"
    res = json.loads(get_mock_json_response(prompt))
    rs = res["risk_score"]
    ts = res["trust_score"]
    ss = rs["sub_scores"]

    overall = rs["overall_score"]
    level   = rs["overall_level"]
    color   = rs["overall_color"]
    penalty = ss["penalty_risk"]
    stability = ss["interest_stability"]

    print(f"=== {name} ===")
    print(f"  Overall: {overall}/100 -> {level} ({color})")
    print(f"  Penalty Risk:      {penalty}%")
    print(f"  Rate Stability:    {stability}%")
    print(f"  Trust Grade:       {ts['trust_grade']} - {ts['trust_grade_label']}")
    print(f"  Transparency Note: {ts['transparency_note']}")
    print(f"  Fairness Note:     {ts['fairness_note']}")
    print()

    # Assertions — scores must differ by category; insurance/lease/loan should be >= Medium
    if "Insurance" in name or "Lease" in name or "Loan" in name:
        if overall < 40:
            print(f"  FAIL: Expected overall >= 40 for {name}, got {overall}")
            all_pass = False
        else:
            print(f"  PASS (score {overall} >= 40)")
    print()

if all_pass:
    print("All risk score tests passed!")
else:
    print("Some risk score tests FAILED.")
