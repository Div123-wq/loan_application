"""End-to-end API test: upload insurance doc → analyze → verify dashboard JSON."""
import sys, io, json, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://127.0.0.1:5000"

HEALTH_DOC = b"""HEALTH INSURANCE POLICY DOCUMENT

Insurer: ICICI Lombard Health Insurance
Policyholder: Rahul Verma
Date: 12 May 2026

Sum Insured: 3,00,000 INR

Annual Premium: 7,200 INR per year

TERMS AND CONDITIONS:
The insured agrees to a mandatory co-payment ratio of 20% on all specialized surgery treatments and hospitalizations.
Hospital room rent charges are capped at a strict sub-limit of 1% of the overall Sum Insured per day.
A mandatory waiting period of 36 months applies to all claims related to diabetes, hypertension, and joint treatments.
Pre-existing diseases are excluded for the first 24 months of the policy.
"""

AUTO_DOC = b"""COMPREHENSIVE MOTOR INSURANCE POLICY

Insurer: Bajaj Allianz General Insurance
Policyholder Name: Priya Mehta
Policy Date: 10 May 2026

Coverage: Rs. 8,00,000
Annual Premium: Rs. 12,000

TERMS:
Depreciation rates of up to 50% shall apply on nylon, plastic, rubber parts and batteries replaced during vehicle repair claims.
A compulsory deductible excess of Rs. 2,000 shall be borne by the insured for every separate claim event.
Reimbursements for repairs undertaken at non-network garages are restricted to 70% of standard estimated surveyor repair costs.
"""

def multipart_upload(filename, content, content_type="text/plain"):
    boundary = b"----FormBoundary7MA4YWxkTrZu0gW"
    body = (
        b"--" + boundary + b"\r\n"
        b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n'
        b"Content-Type: " + content_type.encode() + b"\r\n\r\n"
        + content + b"\r\n"
        b"--" + boundary + b"--\r\n"
    )
    req = urllib.request.Request(
        BASE + "/api/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary.decode()}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def analyze(doc_id):
    req = urllib.request.Request(
        BASE + f"/api/analyze/{doc_id}",
        data=b"",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


print("=" * 60)
print("TEST 1: Health Insurance document")
print("=" * 60)
up = multipart_upload("health_insurance.txt", HEALTH_DOC)
print(f"Upload OK  → doc_id: {up['doc_id']}, chars: {up['extracted_chars']}")

an = analyze(up["doc_id"])
ci = an["core_info"]
print(f"Category   : {ci['loan_type']}")
print(f"Insurer    : {ci['lender_name']}")
print(f"Policyholder: {ci['borrower_name']}")
print(f"Sum Insured: {ci['loan_amount']}")
print(f"Premium    : {ci['interest_rate']}")
print(f"EMI/mo     : {ci['emi_amount']}")
print(f"Summary    : {ci['summary'][:120]}...")
print(f"Traps      : {[t['title'] for t in an['hidden_traps']]}")

assert "insurance" in ci["loan_type"].lower(), f"FAIL: wrong type {ci['loan_type']}"
assert ci["loan_amount"] not in ("", None, "₹25,00,000"), f"FAIL: amount not extracted, got {ci['loan_amount']}"
assert "Lombard" in ci["lender_name"] or "ICICI" in ci["lender_name"], f"FAIL: wrong lender {ci['lender_name']}"
assert len(an["hidden_traps"]) >= 2, "FAIL: no traps"
print("✅ PASS")

print()
print("=" * 60)
print("TEST 2: Auto Insurance document")
print("=" * 60)
up2 = multipart_upload("auto_insurance.txt", AUTO_DOC)
print(f"Upload OK  → doc_id: {up2['doc_id']}, chars: {up2['extracted_chars']}")

an2 = analyze(up2["doc_id"])
ci2 = an2["core_info"]
print(f"Category   : {ci2['loan_type']}")
print(f"Insurer    : {ci2['lender_name']}")
print(f"Coverage   : {ci2['loan_amount']}")
print(f"Premium    : {ci2['interest_rate']}")
print(f"Traps      : {[t['title'] for t in an2['hidden_traps']]}")

assert "insurance" in ci2["loan_type"].lower(), f"FAIL: wrong type {ci2['loan_type']}"
assert ci2["loan_amount"] not in ("", None), f"FAIL: amount blank"
assert any("Depreciation" in t["title"] or "Deductible" in t["title"] for t in an2["hidden_traps"]), "FAIL: expected auto traps"
print("✅ PASS")

print()
print("All end-to-end API tests passed! ✅")
