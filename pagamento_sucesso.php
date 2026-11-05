<?php
session_start();

// Verifica se há uma transação paga na sessão
$transactionId = $_SESSION['transaction_id'] ?? '';
$status = $_SESSION['transaction_status'] ?? '';

// Se não tem transação paga, redireciona para início
if (empty($transactionId) || $status !== 'PAID') {
    header('Location: index.html');
    exit;
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento Confirmado - Mercado Livre</title>
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
        .success-icon {
            font-size: 60px;
            color: #28a745;
            margin-bottom: 20px;
        }
        h2 {
            color: #28a745;
            margin-bottom: 10px;
        }
        .info-box {
            background: #d4edda;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .info-item span:first-child {
            font-weight: bold;
        }
        .instructions {
            text-align: left;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3483fa;
        }
        .instructions h3 {
            color: #3483fa;
            margin-bottom: 10px;
        }
        .instructions ol {
            padding-left: 20px;
        }
        .instructions li {
            margin-bottom: 8px;
        }
        .next-steps {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }
        .btn {
            display: block;
            background: #3483fa;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #2968c8;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        
        <div class="success-icon">✓</div>
        
        <h2>Pagamento Confirmado!</h2>
        <p>Sua taxa de liberação foi paga com sucesso.</p>
        
        <div class="info-box">
            <div class="info-item">
                <span>Status:</span>
                <span>CONFIRMADO</span>
            </div>
            <div class="info-item">
                <span>ID da Transação:</span>
                <span><?php echo substr($transactionId, 0, 12) . '...'; ?></span>
            </div>
            <div class="info-item">
                <span>Data/Hora:</span>
                <span><?php echo date('d/m/Y H:i:s'); ?></span>
            </div>
            <div class="info-item">
                <span>Valor:</span>
                <span>R$ 124,08</span>
            </div>
        </div>
        
        <div class="instructions">
            <h3>Próximos Passos:</h3>
            <ol>
                <li>Seu pedido será liberado automaticamente</li>
                <li>O rastreamento será atualizado em até 15 minutos</li>
                <li>Você receberá um email com os detalhes da entrega</li>
                <li>O entregador entrará em contato para agendar</li>
            </ol>
        </div>
        
        <div class="next-steps">
            ⚠️ <strong>Atenção:</strong> Mantenha seu celular próximo, pois o entregador pode ligar para confirmar o endereço.
        </div>
        
        <a href="index3.html" class="btn">Voltar para Rastreamento</a>
        <a href="index.html" class="btn btn-secondary">Novo Rastreamento</a>
        
        <div style="margin-top: 20px; font-size: 12px; color: #666;">
            <p>Em caso de dúvidas, entre em contato com nosso suporte:</p>
            <p>📞 (11) 99999-9999 | 📧 suporte@mercadolivre.com</p>
        </div>
    </div>
    
    <script>
        // Limpa a sessão após mostrar a página (opcional)
        setTimeout(() => {
            fetch('limpar_sessao.php')
                .then(response => response.json())
                .then(data => {
                    console.log('Sessão limpa');
                })
                .catch(error => {
                    console.error('Erro ao limpar sessão:', error);
                });
        }, 30000); // Limpa após 30 segundos
    </script>
</body>
</html>