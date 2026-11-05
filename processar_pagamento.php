<?php
require_once 'anubispay_config.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método não permitido']);
    exit;
}

// Coleta os dados do formulário
$cpf = $_POST['cpf'] ?? '';
$nome = $_POST['nome'] ?? '';
$email = $_POST['email'] ?? '';
$telefone = $_POST['telefone'] ?? '';

// Validação básica
if (empty($cpf) || empty($nome) || empty($email) || empty($telefone)) {
    http_response_code(400);
    echo json_encode(['error' => 'Todos os campos são obrigatórios']);
    exit;
}

// Limpa o telefone (mantém apenas números)
$telefone = preg_replace('/[^0-9]/', '', $telefone);
if (strlen($telefone) < 10 || strlen($telefone) > 11) {
    http_response_code(400);
    echo json_encode(['error' => 'Telefone inválido']);
    exit;
}

// Limpa o CPF
$cpf = preg_replace('/[^0-9]/', '', $cpf);
if (strlen($cpf) !== 11) {
    http_response_code(400);
    echo json_encode(['error' => 'CPF inválido']);
    exit;
}

// Validação de email
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['error' => 'Email inválido']);
    exit;
}

// Prepara os dados para a AnubisPay
$paymentData = [
    'cpf' => $cpf,
    'name' => $nome,
    'email' => $email,
    'phone' => $telefone
];

// Cria a transação PIX
$result = createPixTransaction($paymentData);

if ($result['success']) {
    $transactionData = $result['data'];
    
    // Salva informações da transação na sessão (simulado)
    session_start();
    $_SESSION['transaction_id'] = $transactionData['id'];
    $_SESSION['transaction_status'] = $transactionData['status'];
    $_SESSION['pix_qr_code'] = $transactionData['pix']['qr_code'] ?? '';
    $_SESSION['pix_expiration'] = $transactionData['pix']['expiration_date'] ?? '';
    
    // Retorna os dados para o frontend
    echo json_encode([
        'success' => true,
        'transaction_id' => $transactionData['id'],
        'qr_code' => $transactionData['pix']['qr_code'] ?? '',
        'expiration_date' => $transactionData['pix']['expiration_date'] ?? '',
        'status' => $transactionData['status'],
        'amount' => $transactionData['amount'] / 100, // Converte para reais
        'redirect_url' => 'pix_anubispay.php?transaction_id=' . $transactionData['id']
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $result['error'] ?? 'Erro ao criar transação',
        'debug' => $result['raw'] ?? null
    ]);
}
?>