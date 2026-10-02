import os
import json
import base64
import mimetypes
import requests
from pathlib import Path


# =========================
# KONFIGURASI
# =========================

IMAGE = Path("data/raw/nota.png")

MODEL = os.environ["LM_STUDIO_MODEL"]

API_URL = "http://172.25.176.1:1234/api/v1/chat"


# =========================
# CEK FILE
# =========================

if not IMAGE.exists():
    raise FileNotFoundError(
        f"Gambar tidak ditemukan: {IMAGE}"
    )


# =========================
# DETEKSI JENIS GAMBAR
# =========================

mime_type, _ = mimetypes.guess_type(IMAGE)

allowed_types = {
    "image/png",
    "image/jpeg",
    "image/webp"
}

if mime_type not in allowed_types:
    raise ValueError(
        f"Format gambar tidak didukung: {mime_type}\n"
        "Gunakan PNG, JPG/JPEG, atau WEBP."
    )

print(f"File       : {IMAGE}")
print(f"Format     : {mime_type}")


# =========================
# GAMBAR -> BASE64
# =========================

with open(IMAGE, "rb") as f:
    image_base64 = base64.b64encode(
        f.read()
    ).decode("utf-8")

# MIME type otomatis mengikuti file
image_data_url = (
    f"data:{mime_type};base64,{image_base64}"
)


# =========================
# REQUEST KE LM STUDIO
# =========================

payload = {
    "model": MODEL,
    "input": [
        {
            "type": "text",
            "content": (
                "Baca nota pada gambar. "
                "Ekstrak merchant, tanggal, item, "
                "subtotal, pajak, dan total. "
                "Keluarkan hanya JSON valid tanpa markdown. "
                "Jika pajak tidak terlihat, isi 0. "
                "Jangan mengarang."
            )
        },
        {
            "type": "image",
            "data_url": image_data_url
        }
    ]
}


response = requests.post(
    API_URL,
    json=payload,
    timeout=180
)

print("STATUS     :", response.status_code)

if response.status_code != 200:
    print("RESPONSE:", response.text)
    response.raise_for_status()


# =========================
# AMBIL RESPONSE
# =========================

data = response.json()

content = None

for output in data.get("output", []):
    if output.get("type") == "message":
        content = output.get("content")
        break

if content is None:
    raise ValueError(
        "Content tidak ditemukan pada response LM Studio."
    )


# =========================
# BERSIHKAN JSON
# =========================

content = content.strip()

if content.startswith("```json"):
    content = content[7:]

if content.startswith("```"):
    content = content[3:]

if content.endswith("```"):
    content = content[:-3]

content = content.strip()

result = json.loads(content)


# =========================
# SIMPAN HASIL
# =========================

Path("reports").mkdir(
    parents=True,
    exist_ok=True
)

output_file = Path("reports/receipt.json")

output_file.write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# =========================
# OUTPUT
# =========================

print("\nHASIL EKSTRAKSI:")

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

print(
    f"\nBerhasil disimpan ke: {output_file}"
)
