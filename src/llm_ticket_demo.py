import os
import requests

MODEL = os.environ["LM_STUDIO_MODEL"]

url = "http://172.25.176.1:1234/v1/chat/completions"

prompt = """Jawab JSON dengan kunci summary, priority, reason, missing_info.
Tiket: Pembayaran gagal dan saldo terpotong."""

response = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json={
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    },
    timeout=120
)

response.raise_for_status()

result = response.json()

print(result["choices"][0]["message"]["content"])
