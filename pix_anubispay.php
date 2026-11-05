<?php
require_once 'anubispay_config.php';

$transactionId = $_GET['transaction_id'] ?? '';

if (empty($transactionId)) {
    // Se não tem transaction_id, tenta buscar da sessão
    session_start();
    $transactionId = $_SESSION['transaction_id'] ?? '';
}

if (empty($transactionId)) {
    header('Location: index.html');
    exit;
}

// Busca informações da transação
$transactionInfo = getTransactionInfo($transactionId);

if (!$transactionInfo['success']) {
    // Se não conseguiu buscar, usa dados da sessão
    session_start();
    $qrCode = $_SESSION['pix_qr_code'] ?? '';
    $expirationDate = $_SESSION['pix_expiration'] ?? '';
    $status = $_SESSION['transaction_status'] ?? 'PENDING';
    $amount = 124.08; // Valor padrão
} else {
    $data = $transactionInfo['data'];
    $qrCode = $data['pix']['qr_code'] ?? '';
    $expirationDate = $data['pix']['expiration_date'] ?? '';
    $status = $data['status'] ?? 'PENDING';
    $amount = isset($data['amount']) ? $data['amount'] / 100 : 124.08;
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento PIX - AnubisPay</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 20px;
        }
        h2 {
            color: #3483fa;
            margin-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        .status-paid {
            background: #d4edda;
            color: #155724;
        }
        .info-box {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .info-item span:first-child {
            color: #666;
        }
        .qr-code-container {
            background: #fff;
            border: 2px dashed #ddd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .qr-code-placeholder {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            background: #f0f0f0;
            border-radius: 5px;
            color: #666;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            width: 100%;
        }
        .pix-code {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            margin: 15px 0;
            text-align: center;
            max-height: 100px;
            overflow-y: auto;
        }
        .copy-btn {
            background: #3483fa;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            width: 100%;
        }
        .copy-btn:hover {
            background: #2968c8;
        }
        .timer {
            font-size: 18px;
            font-weight: bold;
            color: #dc3545;
            margin: 15px 0;
        }
        .note {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn {
            flex: 1;
            padding: 10px;
            border-radius: 5px;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }
        .btn-primary {
            background: #3483fa;
            color: white;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        <h2>Pagamento PIX</h2>
        
        <div class="status-badge status-<?php echo strtolower($status); ?>">
            <?php 
            $statusText = [
                'PENDING' => 'AGUARDANDO PAGAMENTO',
                'PAID' => 'PAGAMENTO REALIZADO',
                'EXPIRED' => 'EXPIRADO',
                'REFUSED' => 'RECUSADO',
                'ERROR' => 'ERRO'
            ];
            echo $statusText[$status] ?? $status;
            ?>
        </div>
        
        <div class="info-box">
            <div class="info-item">
                <span>Valor:</span>
                <span>R$ <?php echo number_format($amount, 2, ',', '.'); ?></span>
            </div>
            <div class="info-item">
                <span>ID da Transação:</span>
                <span><?php echo substr($transactionId, 0, 12) . '...'; ?></span>
            </div>
            <div class="info-item">
                <span>Status:</span>
                <span><?php echo $status; ?></span>
            </div>
            <?php if ($expirationDate): ?>
            <div class="info-item">
                <span>Expira em:</span>
                <span><?php echo date('d/m/Y H:i', strtotime($expirationDate)); ?></span>
            </div>
            <?php endif; ?>
        </div>
        
        <div class="qr-code-container">
            <?php if (!empty($qrCode)): ?>
                <div id="qrcode"></div>
                <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
                <script>
                    QRCode.toCanvas(document.createElement('canvas'), '<?php echo addslashes($qrCode); ?>', function(error, canvas) {
                        if (error) {
                            document.getElementById('qrcode').innerHTML = '<div class="qr-code-placeholder">Erro ao gerar QR Code</div>';
                        } else {
                            document.getElementById('qrcode').innerHTML = '';
                            document.getElementById('qrcode').appendChild(canvas);
                        }
                    });
                </script>
            <?php else: ?>
                <div class="qr-code-placeholder">
                    QR Code não disponível<br>
                    <small>Transação ID: <?php echo substr($transactionId, 0, 8); ?>...</small>
                </div>
            <?php endif; ?>
        </div>
        
        <?php if (!empty($qrCode)): ?>
        <div class="pix-code" id="pixCode">
            <?php echo htmlspecialchars($qrCode); ?>
        </div>
        
        <button class="copy-btn" onclick="copyPixCode()">Copiar código PIX</button>
        <?php endif; ?>
        
        <div class="timer" id="timer">02:00</div>
        
        <div class="action-buttons">
            <a href="javascript:void(0);" onclick="checkPaymentStatus()" class="btn btn-primary">Verificar Pagamento</a>
            <a href="index.html" class="btn btn-secondary">Voltar ao Início</a>
        </div>
        
        <div class="note">
            ⚠️ Este é um sistema de pagamento real integrado com AnubisPay.
            <br><br>
            <strong>Instruções:</strong>
            <ol style="text-align: left; margin-top: 10px; padding-left: 20px;">
                <li>Escaneie o QR Code com seu app de banco</li>
                <li>Ou copie o código PIX e cole no seu app</li>
                <li>O pagamento expira em 24 horas</li>
                <li>Após o pagamento, clique em "Verificar Pagamento"</li>
            </ol>
        </div>
    </div>
    
    <script>
        function copyPixCode() {
            const pixCode = document.getElementById('pixCode');
            const textArea = document.createElement('textarea');
            textArea.value = pixCode.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('Código PIX copiado para a área de transferência!');
        }
        
        // Timer de 2 minutos para auto-refresh
        let timeLeft = 120;
        const timerElement = document.getElementById('timer');
        
        function updateTimer() {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft > 0) {
                timeLeft--;
                setTimeout(updateTimer, 1000);
            } else {
                timerElement.textContent = "ATUALIZANDO...";
                checkPaymentStatus();
                timeLeft = 120; // Reseta o timer
                updateTimer();
            }
        }
        
        function checkPaymentStatus() {
            timerElement.textContent = "VERIFICANDO...";
            
            fetch('verificar_pagamento.php?transaction_id=<?php echo $transactionId; ?>')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.status === 'PAID') {
                            alert('Pagamento confirmado! Seu pedido será liberado em breve.');
                            window.location.href = 'pagamento_sucesso.php';
                        } else if (data.status === 'EXPIRED') {
                            alert('Pagamento expirado. Por favor, inicie um novo pagamento.');
                            window.location.href = 'confirmar.php';
                        } else {
                            alert('Pagamento ainda pendente. Aguarde e tente novamente em alguns instantes.');
                            timerElement.textContent = "02:00";
                            timeLeft = 120;
                        }
                    } else {
                        alert('Erro ao verificar pagamento: ' + (data.error || 'Desconhecido'));
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro ao verificar pagamento. Tente novamente.');
                    timerElement.textContent = "02:00";
                    timeLeft = 120;
                });
        }
        
        // Inicia o timer
        updateTimer();
        
        // Verifica automaticamente a cada 30 segundos
        setInterval(checkPaymentStatus, 30000);
    </script>
</body>
</html>