#!/bin/bash

echo "=== Teste de Fluxo AnubisPay ==="
echo

# 1. Testar API de CPF
echo "1. Testando API de CPF..."
curl -X POST "http://127.0.0.1:8099/processar_cpf.php" -d "cpf=11144477735" | jq -c '{nome: .nome, cpf: .cpf}'
echo

# 2. Testar criação de pagamento
echo "2. Testando criação de pagamento..."
TRANSACTION_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8099/processar_pagamento.php" \
  -d "cpf=11144477735&nome=Jean%20Carlos%20Monteiro&email=teste@exemplo.com&telefone=11999999999")

echo "$TRANSACTION_RESPONSE" | jq -c '{success: .success, transaction_id: .transaction_id, redirect_url: .redirect_url}'

TRANSACTION_ID=$(echo "$TRANSACTION_RESPONSE" | jq -r '.transaction_id')
echo "Transaction ID: $TRANSACTION_ID"
echo

# 3. Testar página do PIX
echo "3. Testando página do PIX..."
curl -s "http://127.0.0.1:8099/pix_anubispay.php?transaction_id=$TRANSACTION_ID" | grep -o "<title>[^<]*</title>"
echo

# 4. Testar verificação de pagamento
echo "4. Testando verificação de pagamento..."
curl -s "http://127.0.0.1:8099/verificar_pagamento.php?transaction_id=$TRANSACTION_ID" | jq -c '{success: .success, status: .status}'
echo

# 5. Testar webhook (simulação)
echo "5. Testando webhook..."
curl -s -X POST "http://127.0.0.1:8099/webhook.php" \
  -H "Content-Type: application/json" \
  -d '{"Id":"test_id","Status":"PAID","Amount":124.08,"PaidAt":"2026-01-06T23:41:02.000Z"}' | jq -c '{received: .received, message: .message}'
echo

echo "=== Teste Concluído ==="
echo
echo "URLs para testar manualmente:"
echo "1. Página inicial: http://127.0.0.1:8099/index.html"
echo "2. CPF de teste: 11144477735"
echo "3. Email de teste: teste@exemplo.com"
echo "4. Telefone de teste: 11999999999"
echo
echo "Logs disponíveis em:"
echo "- server.log (servidor Python)"
echo "- webhook.log (webhooks recebidos)"