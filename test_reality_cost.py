import urllib.request, json
HEALTH_DOC = b'''HEALTH INSURANCE POLICY DOCUMENT\nInsurer: ICICI Lombard\nSum Insured: 3,00,000 INR\nAnnual Premium: 7,200 INR per year'''
boundary = b'----FormBoundary7MA4YWxkTrZu0gW'
body = (b'--' + boundary + b'\r\n' + b'Content-Disposition: form-data; name="file"; filename="test.txt"\r\nContent-Type: text/plain\r\n\r\n' + HEALTH_DOC + b'\r\n--' + boundary + b'--\r\n')
req = urllib.request.Request('http://127.0.0.1:5000/api/upload', data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary.decode()}'}, method='POST')
doc_id = json.loads(urllib.request.urlopen(req).read())['doc_id']

req = urllib.request.Request(f'http://127.0.0.1:5000/api/analyze/{doc_id}', data=b'', headers={'Content-Type': 'application/json'}, method='POST')
res = json.loads(urllib.request.urlopen(req).read())
print(json.dumps(res['reality_cost'], indent=2))
print("CORE_INFO keys:")
print(list(res['core_info'].keys()))
