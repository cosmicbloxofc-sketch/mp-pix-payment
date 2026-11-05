# Integração AnubisPay - Sistema de Pagamento

Este projeto foi integrado com a API da AnubisPay para processamento de pagamentos PIX reais.

## 📋 Visão Geral

O sistema agora inclui:
1. **Consulta de CPF** via API externa (suapendencia.org)
2. **Processamento de pagamentos** via AnubisPay
3. **Webhooks** para atualizações de status
4. **Interface completa** para geração de PIX

## 🔑 Chaves de API

As chaves da AnubisPay estão configuradas em `anubispay_config.php`:

- **Public Key:** `anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0`
- **Secret Key:** `Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ`

## 📁 Estrutura de Arquivos

### Arquivos Principais

1. **`anubispay_config.php`** - Configuração da API AnubisPay
2. **`processar_pagamento.php`** - Endpoint para criar transações PIX
3. **`pix_anubispay.php`** - Página para mostrar QR Code PIX
4. **`verificar_pagamento.php`** - Verifica status da transação
5. **`webhook.php`** - Recebe atualizações da AnubisPay
6. **`pagamento_sucesso.php`** - Página de confirmação
7. **`limpar_sessao.php`** - Limpa dados da sessão

### Arquivos Modificados

1. **`confirmar.php`** - Atualizado para usar AJAX e AnubisPay
2. **`server.py`** - Atualizado para suportar novos endpoints

## 🔄 Fluxo do Sistema

### Fluxo Normal
1. Usuário insere CPF → `processar_cpf.php`
2. Dados validados → Redireciona para `confirmar.php`
3. Usuário preenche email/telefone → `processar_pagamento.php`
4. Cria transação AnubisPay → `pix_anubispay.php`
5. Mostra QR Code → Usuário paga
6. Webhook atualiza status → `pagamento_sucesso.php`

### Fluxo de Verificação
1. Página PIX verifica automaticamente a cada 30s
2. Usuário pode clicar em "Verificar Pagamento"
3. `verificar_pagamento.php` consulta status na AnubisPay

## ⚙️ Configuração

### Ambiente de Produção
Para usar em produção:

1. **Atualize as chaves** no `anubispay_config.php`
2. **Configure o webhook** no painel da AnubisPay
3. **Habilite SSL** no servidor
4. **Use variáveis de ambiente** para as chaves

### Endpoints da API AnubisPay
- **Base URL:** `https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net`
- **Criar transação:** `POST /v1/payment-transaction/create`
- **Consultar transação:** `GET /v1/payment-transaction/info/{id}`

## 🔒 Segurança

### Implementado
1. **Validação de campos** (CPF, email, telefone)
2. **Autenticação Basic Auth** com base64
3. **Sessões PHP** para estado da transação
4. **Logging** de webhooks

### Recomendações para Produção
1. **Use HTTPS** em todos os endpoints
2. **Valide IPs** dos webhooks
3. **Implemente rate limiting**
4. **Use banco de dados** para armazenar transações
5. **Criptografe dados sensíveis**

## 🧪 Testes

### Testar Integração
```bash
# Testar API de CPF
curl -X POST "http://localhost:8099/processar_cpf.php" -d "cpf=11144477735"

# Testar criação de pagamento
curl -X POST "http://localhost:8099/processar_pagamento.php" \
  -d "cpf=11144477735&nome=Teste&email=teste@exemplo.com&telefone=11999999999"

# Testar verificação
curl "http://localhost:8099/verificar_pagamento.php?transaction_id=ID_DA_TRANSACAO"
```

### Status de Transações
- **PENDING** - Aguardando pagamento
- **PAID** - Pagamento confirmado
- **EXPIRED** - Pagamento expirado
- **REFUSED** - Pagamento recusado
- **ERROR** - Erro na transação

## 📝 Logs

### Webhook Logs
Os webhooks são logados em `webhook.log` com:
- Timestamp
- Headers da requisição
- Dados recebidos
- Status processado

### Server Logs
O servidor Python loga em `server.log`:
- Erros de API
- Requisições processadas
- Status de conexão

## 🚀 Implantação

### Passos para Produção
1. **Configure um servidor web** (Apache/Nginx) com PHP 8+
2. **Instale dependências:** `curl`, `openssl`
3. **Configure SSL** com certificado válido
4. **Atualize URLs** no `anubispay_config.php`
5. **Configure webhook** no painel AnubisPay
6. **Teste fluxo completo** com valores baixos

### Monitoramento
1. **Verifique logs** regularmente
2. **Monitore status** das transações
3. **Configure alertas** para erros
4. **Mantenha backup** das transações

## 🆘 Troubleshooting

### Problemas Comuns

1. **Erro 403 na API de CPF**
   - Verifique user-agent na requisição
   - Teste diretamente no navegador

2. **Erro de autenticação AnubisPay**
   - Verifique chaves no `anubispay_config.php`
   - Teste autenticação com curl exemplo

3. **QR Code não aparece**
   - Verifique se a biblioteca QR Code está carregada
   - Confira se o JavaScript está habilitado

4. **Webhook não recebido**
   - Verifique URL no painel AnubisPay
   - Confira logs em `webhook.log`
   - Teste endpoint manualmente

### Suporte
Para questões técnicas:
1. Consulte a [documentação da AnubisPay](https://anubispay.com/docs)
2. Verifique logs do sistema
3. Teste endpoints individualmente

## 📄 Licença

Este projeto é para fins educacionais e de demonstração. Use em produção por sua própria conta e risco.

---

**Nota:** Em ambiente de desenvolvimento, o servidor Python simula algumas funcionalidades. Em produção, substitua pela integração real com a API AnubisPay.