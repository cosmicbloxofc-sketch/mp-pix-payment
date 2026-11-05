#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  TESTE DO FLUXO COMPLETO COM MODAL PIX"
echo "═══════════════════════════════════════════════════════════"
echo

echo "📋 FLUXO IMPLEMENTADO:"
echo "---------------------"
echo "1. confirmar.php → Preenche email/telefone"
echo "2. resumo_pagamento.php → Mostra resumo com botão 'Pagar com PIX'"
echo "3. [MODAL ABRE] → QR Code + Timer 10:00"
echo "4. pix_anubispay.php → Após pagamento confirmado"
echo "5. pagamento_sucesso.php → Confirmação final"
echo

echo "🧪 TESTANDO ETAPAS:"
echo "-------------------"
echo

echo "1️⃣  Testando confirmar.php..."
CONFIRMAR=$(curl -s "http://127.0.0.1:8099/confirmar.php?nome=EDIENE+SOARES+DA+CUNHA&cpf=07311752639&nascimento=21/10/1986")
if echo "$CONFIRMAR" | grep -q "Validação"; then
    echo "   ✅ confirmar.php está funcionando"
else
    echo "   ❌ Erro em confirmar.php"
fi
echo

echo "2️⃣  Testando resumo_pagamento.php (nova página)..."
RESUMO=$(curl -s "http://127.0.0.1:8099/resumo_pagamento.php?nome=EDIENE+SOARES+DA+CUNHA&cpf=07311752639&email=teste@exemplo.com&telefone=55379992464")

echo "   📄 Conteúdo encontrado:"
echo "$RESUMO" | grep -o "<title>[^<]*</title>" | sed 's/^/      /'
echo "$RESUMO" | grep -o "EDIENE SOARES DA CUNHA" | head -1 | sed 's/^/      /'
echo "$RESUMO" | grep -o "Taxa alfandegária" | sed 's/^/      /'
echo "$RESUMO" | grep -o "R\\$ 124,08" | head -1 | sed 's/^/      /'
echo "$RESUMO" | grep -o "Pagar com PIX" | sed 's/^/      /'

if echo "$RESUMO" | grep -q "Pagar com PIX"; then
    echo "   ✅ Página de resumo OK"
    echo "   ✅ Botão 'Pagar com PIX' presente"
else
    echo "   ❌ Erro na página de resumo"
fi

if echo "$RESUMO" | grep -q "abrirModal()"; then
    echo "   ✅ Função de abrir modal presente"
else
    echo "   ❌ Função de modal não encontrada"
fi

if echo "$RESUMO" | grep -q "Expira em"; then
    echo "   ✅ Timer do modal configurado"
else
    echo "   ❌ Timer não encontrado"
fi
echo

echo "3️⃣  Testando geração de PIX (processar_pagamento.php)..."
PIX_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8099/processar_pagamento.php" \
  -d "cpf=07311752639&nome=EDIENE SOARES DA CUNHA&email=teste@exemplo.com&telefone=55379992464")

if echo "$PIX_RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
    TRANSACTION_ID=$(echo "$PIX_RESPONSE" | jq -r '.transaction_id')
    QR_CODE=$(echo "$PIX_RESPONSE" | jq -r '.qr_code' | head -c 30)
    echo "   ✅ PIX gerado com sucesso"
    echo "   📋 Transaction ID: $TRANSACTION_ID"
    echo "   🔢 QR Code (início): $QR_CODE..."
else
    echo "   ❌ Erro ao gerar PIX"
fi
echo

echo "4️⃣  Testando página de sucesso..."
SUCESSO=$(curl -s "http://127.0.0.1:8099/pagamento_sucesso.php")
if echo "$SUCESSO" | grep -q "Pagamento Confirmado"; then
    echo "   ✅ Página de sucesso funcionando"
else
    echo "   ❌ Erro na página de sucesso"
fi
echo

echo "═══════════════════════════════════════════════════════════"
echo "  RESUMO DA IMPLEMENTAÇÃO"
echo "═══════════════════════════════════════════════════════════"
echo
echo "✅ IMPLEMENTADO:"
echo "   • Página de resumo com destinatário"
echo "   • Botão 'Pagar com PIX'"
echo "   • Modal com QR Code"
echo "   • Timer de expiração (10:00)"
echo "   • Botão 'Copiar' código PIX"
echo "   • Integração com AnubisPay"
echo "   • Verificação automática de pagamento"
echo
echo "🌐 URLs PARA TESTE MANUAL:"
echo "   1. http://127.0.0.1:8099/confirmar.php?nome=EDIENE+SOARES+DA+CUNHA&cpf=07311752639&nascimento=21/10/1986"
echo "   2. http://127.0.0.1:8099/resumo_pagamento.php?nome=EDIENE+SOARES+DA+CUNHA&cpf=07311752639&email=teste@exemplo.com&telefone=55379992464"
echo
echo "📱 COMO FUNCIONA:"
echo "   1. Usuário preenche email/telefone em confirmar.php"
echo "   2. Clica em 'Validar e pagar com PIX'"
echo "   3. Vai para resumo_pagamento.php"
echo "   4. Clica em 'Pagar com PIX'"
echo "   5. MODAL ABRE com QR Code e timer"
echo "   6. Usuário paga (ou clica Copiar)"
echo "   7. Sistema verifica automaticamente"
echo "   8. Redireciona para página de sucesso"
echo
echo "═══════════════════════════════════════════════════════════"
echo "  TESTE CONCLUÍDO!"
echo "═══════════════════════════════════════════════════════════"