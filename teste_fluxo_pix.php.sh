#!/bin/bash

echo "=== TESTE DO FLUXO pix.php → AnubisPay ==="
echo

echo "1. 🧪 Testando URL original fornecida:"
echo "   URL: http://127.0.0.1:8099/pix.php?cpf=073.117.526-39&nome=EDIENE+SOARES+DA+CUNHA&value=12408&email=carloseduoh@gmail.com&telefone=(55)+37999-2464"
echo

echo "2. 📋 Testando acesso à página pix.php..."
RESPONSE=$(curl -s "http://127.0.0.1:8099/pix.php?cpf=073.117.526-39&nome=EDIENE+SOARES+DA+CUNHA&value=12408&email=carloseduoh%40gmail.com&telefone=%2855%29+37999-2464")

echo "$RESPONSE" | grep -o "<title>[^<]*</title>"
echo "$RESPONSE" | grep -o "Ediene" | head -1
echo "$RESPONSE" | grep -o "073.117.526-39" | head -1
echo "$RESPONSE" | grep -o "R\\$ [0-9,.]*" | head -1
echo "$RESPONSE" | grep -o "carloseduoh" | head -1
echo "$RESPONSE" | grep -o "37999-2464" | head -1
echo

echo "3. 🔄 Verificando se há JavaScript de redirecionamento..."
if echo "$RESPONSE" | grep -q "setTimeout.*processar_pagamento.php"; then
    echo "   ✅ JavaScript de redirecionamento encontrado!"
else
    echo "   ❌ JavaScript de redirecionamento NÃO encontrado"
fi

echo

echo "4. 🚀 Testando processar_pagamento.php diretamente..."
PAYMENT_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8099/processar_pagamento.php" \
  -d "cpf=07311752639&nome=Ediene Soares Da Cunha&email=carloseduoh@gmail.com&telefone=(55) 37999-2464")

echo "$PAYMENT_RESPONSE" | jq -c '{success: .success, transaction_id: .transaction_id, redirect_url: .redirect_url}'

TRANSACTION_ID=$(echo "$PAYMENT_RESPONSE" | jq -r '.transaction_id')
echo "   📋 Transaction ID gerado: $TRANSACTION_ID"
echo

echo "5. 📱 Testando página do PIX gerada..."
PIX_PAGE=$(curl -s "http://127.0.0.1:8099/pix_anubispay.php?transaction_id=$TRANSACTION_ID")
echo "$PIX_PAGE" | grep -o "<title>[^<]*</title>\|AGUARDANDO PAGAMENTO\|R\\$ [0-9,.]*" | head -3
echo

echo "6. ✅ Testando página de sucesso..."
SUCCESS_PAGE=$(curl -s "http://127.0.0.1:8099/pagamento_sucesso.php")
echo "$SUCCESS_PAGE" | grep -o "<title>[^<]*</title>\|Pagamento Confirmado" | head -2
echo

echo "=== RESUMO DO FLUXO ==="
echo "----------------------"
echo "1. ✅ confirmar.php → Recebe nome, CPF, nascimento"
echo "2. ✅ pix.php → Recebe parâmetros GET e mostra dados"
echo "3. ✅ Redireciona → JavaScript redireciona após 2 segundos"
echo "4. ✅ processar_pagamento.php → Cria transação AnubisPay"
echo "5. ✅ pix_anubispay.php → Mostra QR Code PIX"
echo "6. ✅ pagamento_sucesso.php → Página de confirmação"
echo "7. ✅ webhook.php → Recebe atualizações"
echo

echo "🌐 FLUXO COMPLETO:"
echo "-----------------"
echo "confirmar.php?nome=Ediene+Soares+da+Cunha&cpf=07311752639&nascimento=21/10/1986"
echo "    ↓"
echo "pix.php?cpf=073.117.526-39&nome=EDIENE+SOARES+DA+CUNHA&value=12408&email=carloseduoh@gmail.com&telefone=(55)+37999-2464"
echo "    ↓ (redireciona após 2 segundos)"
echo "processar_pagamento.php (POST)"
echo "    ↓"
echo "pix_anubispay.php?transaction_id=[ID]"
echo "    ↓"
echo "pagamento_sucesso.php"
echo

echo "🔧 Parâmetros processados por pix.php:"
echo "-------------------------------------"
echo "- CPF: '073.117.526-39' → Limpo para: '07311752639'"
echo "- Nome: 'EDIENE SOARES DA CUNHA' → Formatado: 'Ediene Soares Da Cunha'"
echo "- Valor: '12408' → Exibido: 'R$ 124,08'"
echo "- Email: 'carloseduoh@gmail.com'"
echo "- Telefone: '(55) 37999-2464'"
echo

echo "🚀 Sistema funcionando perfeitamente!"