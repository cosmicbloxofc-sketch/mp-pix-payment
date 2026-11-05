<?php
require_once 'anubispay_config.php';

header('Content-Type: application/json; charset=utf-8');

$transactionId = $_GET['transaction_id'] ?? '';

if (empty($transactionId)) {
    echo json_encode(['success' => false, 'error' => 'ID da transação não fornecido']);
    exit;
}

// Busca informações da transação
$result = getTransactionInfo($transactionId);

if ($result['success']) {
    $data = $result['data'];
    
    // Atualiza a sessão
    session_start();
    $_SESSION['transaction_status'] = $data['status'];
    
    if (isset($data['paid_at']) && $data['paid_at']) {
        $_SESSION['paid_at'] = $data['paid_at'];
    }
    
    echo json_encode([
        'success' => true,
        'status' => $data['status'],
        'paid_at' => $data['paid_at'] ?? null,
        'amount' => $data['amount'] ?? 0,
        'refunded_amount' => $data['refunded_amount'] ?? 0,
        'installments' => $data['installments'] ?? 0,
        'payment_method' => $data['payment_method'] ?? ''
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => $result['error'] ?? 'Erro ao buscar transação',
        'status' => 'ERROR'
    ]);
}
?>