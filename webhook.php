<?php
// Webhook da AnubisPay
// Este arquivo recebe atualizações de status das transações

header('Content-Type: application/json; charset=utf-8');

// Log para debug (em produção, remova ou use um sistema de logging apropriado)
$logFile = 'webhook.log';
$logData = [
    'timestamp' => date('Y-m-d H:i:s'),
    'method' => $_SERVER['REQUEST_METHOD'],
    'headers' => getallheaders(),
    'raw_input' => file_get_contents('php://input')
];

// Salva o log
file_put_contents($logFile, json_encode($logData, JSON_PRETTY_UNICODE) . PHP_EOL, FILE_APPEND);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método não permitido']);
    exit;
}

// Obtém os dados do webhook
$webhookData = json_decode(file_get_contents('php://input'), true);

if (empty($webhookData)) {
    http_response_code(400);
    echo json_encode(['error' => 'Dados do webhook inválidos']);
    exit;
}

// Processa os dados do webhook
$transactionId = $webhookData['Id'] ?? '';
$status = $webhookData['Status'] ?? '';
$amount = $webhookData['Amount'] ?? 0;
$paidAt = $webhookData['PaidAt'] ?? '';
$paymentMethod = $webhookData['PaymentMethod'] ?? '';

// Log dos dados recebidos
$webhookLog = [
    'transaction_id' => $transactionId,
    'status' => $status,
    'amount' => $amount,
    'paid_at' => $paidAt,
    'payment_method' => $paymentMethod,
    'full_data' => $webhookData
];

file_put_contents($logFile, "WEBHOOK DATA: " . json_encode($webhookLog, JSON_PRETTY_UNICODE) . PHP_EOL, FILE_APPEND);

// Aqui você pode:
// 1. Atualizar o banco de dados
// 2. Enviar email para o cliente
// 3. Integrar com seu sistema de pedidos
// 4. Notificar outros sistemas

// Exemplo de processamento:
switch ($status) {
    case 'PAID':
        // Pagamento confirmado
        // Atualize o status do pedido para "pago"
        // Envie email de confirmação
        // Libere o produto/serviço
        break;
        
    case 'REFUNDED':
        // Pagamento estornado
        // Atualize o status do pedido para "estornado"
        // Reverta o produto/serviço
        break;
        
    case 'EXPIRED':
        // Pagamento expirado
        // Atualize o status do pedido para "expirado"
        // Permita novo pagamento
        break;
        
    case 'REFUSED':
        // Pagamento recusado
        // Atualize o status do pedido para "recusado"
        // Notifique o cliente
        break;
        
    default:
        // Outros status (PENDING, ERROR, etc.)
        break;
}

// Responde com sucesso
echo json_encode([
    'received' => true,
    'transaction_id' => $transactionId,
    'status' => $status,
    'message' => 'Webhook recebido com sucesso'
]);

// Em produção, você deve verificar a autenticidade do webhook
// usando um segredo compartilhado ou verificando a origem da requisição
?>