from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = dict(urllib.parse.parse_qsl(post_data))
        
        transaction_id = params.get('transaction_id', '')
        
        # Aqui você implementaria a verificação real no AnubisPay
        # Por enquanto, retorna status pendente
        response_data = {
            "success": True,
            "transaction_id": transaction_id,
            "status": "PENDING",
            "paid": False
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
