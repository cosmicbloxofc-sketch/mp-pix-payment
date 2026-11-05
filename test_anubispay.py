import requests
import base64
import json

# Chaves
public_key = "anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0"
secret_key = "Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ"

# Auth
auth_string = f"{public_key}:{secret_key}"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

print(f"Auth String: {auth_string[:50]}...")
print(f"Auth Base64: {auth_base64[:50]}...")

# Payload
payload = {
    "payment_method": "pix",
    "amount": 12408,
    "customer": {
        "name": "Teste Cliente",
        "email": "teste@exemplo.com",
        "document": {
            "type": "cpf",
            "number": "11144477735"
        },
        "phone": "11999999999"
    },
    "items": [
        {
            "title": "Taxa de Teste",
            "unit_price": 12408,
            "quantity": 1,
            "tangible": False
        }
    ],
    "pix": {
        "expires_in_days": 1
    }
}

url = "https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net/v1/payment-transaction/create"

print(f"\nURL: {url}")
print(f"\nPayload: {json.dumps(payload, indent=2)[:200]}...")

response = requests.post(
    url,
    json=payload,
    headers={
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    verify=False,
    timeout=30
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    if data.get('success') and data.get('data'):
        print("\n✅ SUCESSO!")
        print(f"Transaction ID: {data['data'].get('id')}")
        print(f"QR Code (primeiros 50 chars): {data['data'].get('pix', {}).get('qr_code', '')[:50]}")
    else:
        print("\n❌ ERRO na resposta")
        print(f"Errors: {data.get('error_messages')}")
else:
    print(f"\n❌ HTTP {response.status_code}")
