<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$cpf = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['cpf'])) {
        $cpf = $_POST['cpf'];
    } else {
        $input = file_get_contents('php://input');
        if (strpos($input, 'cpf=') === 0) {
            $cpf = substr($input, 4);
        } elseif (strpos($input, '&') !== false) {
            parse_str($input, $params);
            $cpf = $params['cpf'] ?? '';
        }
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['cpf'])) {
    $cpf = $_GET['cpf'];
}

// Limpa o CPF (remove pontos e traços)
$cpf = preg_replace('/[^0-9]/', '', $cpf);

if (strlen($cpf) !== 11) {
    echo json_encode(['error' => 'CPF inválido. Deve conter 11 dígitos.']);
    exit;
}

// API de consulta CPF
$api_url = "https://suapendencia.org/atencao1/api.php?cpf=" . $cpf;

// Configura o contexto para a requisição
$context = stream_context_create([
    'http' => [
        'method' => 'GET',
        'header' => 'Content-Type: application/json',
        'timeout' => 10
    ],
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false
    ]
]);

// Faz a requisição à API
$response = @file_get_contents($api_url, false, $context);

if ($response === FALSE) {
    echo json_encode(['error' => 'Erro ao consultar API de CPF.']);
    exit;
}

$data = json_decode($response, true);

if ($data['status'] == 200 && isset($data['dados'])) {
    $dados = $data['dados'];
    echo json_encode([
        'nome' => $dados['nome'] ?? '',
        'cpf' => $dados['cpf'] ?? $cpf,
        'nascimento' => $dados['data_nascimento'] ?? ''
    ]);
} else {
    echo json_encode(['error' => $data['message'] ?? 'CPF não encontrado na base de dados']);
}
?>