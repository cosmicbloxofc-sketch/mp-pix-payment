from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = dict(urllib.parse.parse_qsl(post_data))
        
        cpf = params.get('cpf', '').replace('.', '').replace('-', '')
        
        if cpf and len(cpf) == 11:
            try:
                # Consulta API de CPF
                api_url = f"https://suapendencia.org/atencao1/api.php?cpf={cpf}"
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    result = {
                        "success": True,
                        "nome": data.get("nome", ""),
                        "cpf": data.get("cpf", cpf),
                        "data_nascimento": data.get("data_nascimento", "")
                    }
                else:
                    result = {"success": False, "error": "Erro ao consultar CPF"}
            except Exception as e:
                result = {"success": False, "error": str(e)}
        else:
            result = {"success": False, "error": "CPF inválido ou não fornecido"}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
