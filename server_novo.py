import http.server
import socketserver
import json
import os
import urllib.parse
import sys

# Importa módulo de pagamento
sys.path.insert(0, os.path.dirname(__file__))
from processar_pagamento_anubispay import processar_pagamento

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8099

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _path(self):
        return urllib.parse.urlparse(self.path).path

    def do_POST(self):
        p = self._path()
        length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(length)
        
        if p.endswith("processar_pagamento.php"):
            # Parse params
            data = raw_data.decode('utf-8')
            params = dict(urllib.parse.parse_qsl(data))
            
            print(f"\n💳 NOVA TRANSAÇÃO")
            print(f"   Nome: {params.get('nome', '')}")
            print(f"   CPF: {params.get('cpf', '')}")
            
            # Processa pagamento
            result = processar_pagamento(params)
            
            print(f"   ✅ Transaction ID: {result['transaction_id']}")
            print(f"   📱 Source: {result['source']}")
            print(f"   💰 QR Code: {result['qr_code'][:50]}...")
            
            return self._send(json.dumps(result), "application/json")
        
        return self._send("ok")

    def log_message(self, *a):
        pass

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"✅ Servidor iniciado: http://127.0.0.1:{PORT}/")
    print(f"📋 Com integração AnubisPay + Fallback")
    httpd.serve_forever()
