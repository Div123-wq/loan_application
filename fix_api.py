import os, glob
for file in glob.glob('frontend/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content.replace(
        "const API = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') || window.location.origin === 'null' ? 'http://localhost:5000' : '';",
        "const API = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') || window.location.origin === 'null' || window.location.protocol === 'file:' ? 'http://localhost:5000' : '';"
    )
    with open(file, 'w', encoding='utf-8') as f:
        f.write(new_content)
