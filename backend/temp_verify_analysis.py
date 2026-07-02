import json
import pathlib
import requests

payload_text = """Star Health Insurance Company
Health Insurance Policy
Policyholder: Rohan Sharma
Sum Insured: ₹5,00,000
Annual Premium: ₹8,500
Waiting Period: 24 months
Exclusions: Pre-existing diseases
"""
path = pathlib.Path('temp_test_insurance.txt')
path.write_text(payload_text, encoding='utf-8')
files = {'file': ('insurance.txt', path.open('rb'), 'text/plain')}
r = requests.post('http://127.0.0.1:5000/api/upload', files=files, timeout=30)
print('UPLOAD', r.status_code)
print(r.text)
data = r.json()
if data.get('success'):
    ar = requests.post(f"http://127.0.0.1:5000/api/analyze/{data['doc_id']}", timeout=30)
    print('ANALYZE', ar.status_code)
    print(json.dumps(ar.json()['core_info'], indent=2, ensure_ascii=False))
