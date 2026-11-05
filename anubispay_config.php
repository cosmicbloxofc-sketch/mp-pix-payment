<?php
// Configurações da AnubisPay
define('ANUBISPAY_BASE_URL', 'https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net');
define('ANUBISPAY_API_VERSION', 'v1');

// Chaves da API (você pode mover essas para variáveis de ambiente)
// PUBLIC_KEY: anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0
// SECRET_KEY: Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ
define('ANUBISPAY_PUBLIC_KEY', 'anubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0');
define('ANUBISPAY_SECRET_KEY', 'Danubispay_live_1H4CMFmBvkmouLHefnZhJTdEHe7x79U0ve_6wkQttCvKgt7EN0uqw4Yj3P1DIkX4puZ');

// Webhook URL (onde receberemos as atualizações)
define('WEBHOOK_BASE_URL', 'http://127.0.0.1:8099');

// Função para gerar o header de autenticação
function getAnubisPayAuthHeader() {
    $authString = ANUBISPAY_PUBLIC_KEY . ':' . ANUBISPAY_SECRET_KEY;
    $base64Auth = base64_encode($authString);
    return "Basic $base64Auth";
}

// Função para criar uma transação PIX
function createPixTransaction($data) {
    $url = ANUBISPAY_BASE_URL . '/' . ANUBISPAY_API_VERSION . '/payment-transaction/create';
    
    // Prepara os dados do cliente
    $customer = [
        'name' => $data['name'],
        'email' => $data['email'],
        'document' => [
            'type' => 'cpf',
            'number' => preg_replace('/[^0-9]/', '', $data['cpf'])
        ],
        'phone' => preg_replace('/[^0-9]/', '', $data['phone'])
    ];
    
    // Prepara os itens
    $items = [
        [
            'title' => 'Taxa de Liberação - Mercado Livre',
            'unit_price' => 12408, // R$ 124,08 em centavos
            'quantity' => 1,
            'tangible' => false,
            'external_ref' => 'taxa_liberacao_' . $data['cpf']
        ]
    ];
    
    // Configuração do PIX
    $pixConfig = [
        'expires_in_days' => 1
    ];
    
    // Postback URL (webhook)
    $postbackUrl = WEBHOOK_BASE_URL . '/webhook.php';
    
    // Monta o payload completo
    $payload = [
        'payment_method' => 'pix',
        'amount' => 12408, // R$ 124,08 em centavos
        'customer' => $customer,
        'items' => $items,
        'pix' => $pixConfig,
        'postback_url' => $postbackUrl,
        'metadata' => [
            'provider_name' => 'Mercado Livre - Taxa de Liberação',
            'cpf' => $data['cpf'],
            'nome' => $data['name']
        ],
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'
    ];
    
    // Headers
    $headers = [
        'Accept: application/json',
        'Content-Type: application/json',
        'Authorization: ' . getAnubisPayAuthHeader()
    ];
    
    // Faz a requisição
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Apenas para desenvolvimento
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($response === false) {
        return [
            'success' => false,
            'error' => 'Erro na comunicação com AnubisPay: ' . $error
        ];
    }
    
    $result = json_decode($response, true);
    
    if ($httpCode == 200 && isset($result['success']) && $result['success']) {
        return [
            'success' => true,
            'data' => $result['data'],
            'raw' => $result
        ];
    } else {
        return [
            'success' => false,
            'error' => isset($result['error_messages']) ? implode(', ', $result['error_messages']) : 'Erro desconhecido',
            'http_code' => $httpCode,
            'raw' => $result
        ];
    }
}

// Função para buscar informações de uma transação
function getTransactionInfo($transactionId) {
    $url = ANUBISPAY_BASE_URL . '/' . ANUBISPAY_API_VERSION . '/payment-transaction/info/' . $transactionId;
    
    $headers = [
        'Accept: application/json',
        'Authorization: ' . getAnubisPayAuthHeader()
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Apenas para desenvolvimento
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($response === false) {
        return [
            'success' => false,
            'error' => 'Erro na comunicação com AnubisPay: ' . $error
        ];
    }
    
    $result = json_decode($response, true);
    
    if ($httpCode == 200) {
        return [
            'success' => true,
            'data' => $result,
            'raw' => $result
        ];
    } else {
        return [
            'success' => false,
            'error' => 'Erro ao buscar transação',
            'http_code' => $httpCode,
            'raw' => $result
        ];
    }
}
?>