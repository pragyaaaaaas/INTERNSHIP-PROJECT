 

import requests
import json

# -------------------------------
#  API CONFIG
# -------------------------------

API_URL = "https://api.openai.com/v1/responses"   # your model endpoint
API_KEY = "ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE"                     # 🔒 never expose real key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# -------------------------------
#  YOUR JSON DATA (Corrected)
# -------------------------------

input_payload = {
    "input_data": [
        {
            "fields": [
                "UDI",
                "Product ID",
                "Type",
                "Air temperature K",
                "Process temperature K",
                "Rotational speed rpm",
                "Torque Nm",
                "Tool wear min"
            ],
            "values": [
                [
                    1,
                    "M14860",
                    "M",
                    298.1,
                    308.6,
                    1551,
                    42.8,
                    0
                ]
            ]
        }
    ]
}

# -------------------------------
#  SEND REQUEST
# -------------------------------

response = requests.post(
    API_URL,
    headers=headers,
    json={
        "model": "gpt-4.1",     # or your fine-tuned model name
        "input": input_payload
    }
)

# -------------------------------
#  SHOW RESPONSE
# -------------------------------
print("\n=== API Response ===\n")
print(response.json())
