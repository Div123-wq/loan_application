import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=token)

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": "Return {\"hello\": \"world\"}"}]
    )
    print("SUCCESS JSON_OBJECT")
except Exception as e:
    print(f"ERROR JSON_OBJECT: {e}")

try:
    response2 = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        messages=[{"role": "user", "content": "Return {\"hello\": \"world\"}"}]
    )
    print("SUCCESS NORMAL")
except Exception as e:
    print(f"ERROR NORMAL: {e}")
