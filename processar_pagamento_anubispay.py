import requests
import base64
import json
import re
import uuid
import time

def processar_pagamento(params):
    """Processa pagamento via AnubisPay ou fallback"""
    
    cpf_limpo = re.sub(r'[^0-9]', '', params.get('cpf', ''))
    nome = params.get('nome', 'Cliente')
    email = params.get('email', f'cpf{cpf_limpo}@temp.com')
    telefone = re.sub(r'[^0-9]', '', params.get('telefone', '11999999999'))
    
    # Gera ID único
    transaction_id = str(uuid.uuid4()).replace('-', '')[:32]
    
    # Tenta AnubisPay primeiro
    try:
        payload = {
            "payment_method": "pix",
            "amount": 12408,
            "customer": {
                "name": nome,
                "email": email,
                "document": {"type": "cpf", "number": cpf_limpo},
                "phone": telefone
            },
            "items": [{
                "title": "Taxa de Liberação",
                "unit_price": 12408,
                "quantity": 1,
                "tangible": False,
                "external_ref": f"taxa_{transaction_id}"
            }],
            "pix": {"expires_in_days": 1}
        }
        
        public_key = "anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0"
        secret_key = "Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ"
        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        
        resp = requests.post(
            "https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net/v1/payment-transaction/create",
            json=payload,
            headers={'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'},
            timeout=15,
            verify=False
        )
        
        if resp.status_code == 200 and resp.json().get('success'):
            data = resp.json()['data']
            return {
                "success": True,
                "transaction_id": data['id'],
                "qr_code": data['pix']['qr_code'],
                "expiration_date": data['pix']['expiration_date'],
                "status": "PENDING",
                "amount": 124.08,
                "source": "anubispay"
            }
    except:
        pass
    
    # Fallback: código único simulado
    timestamp = str(int(time.time()))
    unique = transaction_id[:12]
    qr = f"00020126360014br.gov.bcb.pix0114{unique}{timestamp}520400005303986540512408580258{nome[:25].upper().ljust(25)}6304"
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "qr_code": qr,
        "expiration_date": "2026-01-08T00:00:00+00:00",
        "status": "PENDING",
        "amount": 124.08,
        "source": "simulated"
    }
