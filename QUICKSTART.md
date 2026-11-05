# 🚀 Deploy Rápido na Vercel

## 3 Passos Simples

### 1. Importar na Vercel
- Acesse: https://vercel.com/new
- Selecione o repo: `cosmicbloxofc-sketch/mp-pix-payment`
- Clique: **Import**

### 2. Configurar Variáveis de Ambiente
Adicione no dashboard da Vercel (Settings → Environment Variables):

```
ANUBISPAY_PUBLIC_KEY = [sua_chave_publica]
ANUBISPAY_SECRET_KEY = [sua_chave_secreta]
```

> Obtenha as chaves do AnubisPay no dashboard deles ou entre em contato.

### 3. Deploy
- Clique em **Deploy**
- Aguarde finalizar
- Acesse: https://mp-pix-payment.vercel.app/confirmar.php

---

## ✅ Teste

1. Preencha os dados no formulário
2. Clique "Pagar com PIX"
3. Modal abre com QR Code único
4. Cada clique gera NOVO código! 🎉

---

## 📚 Mais Informações

- Veja `DEPLOY_INSTRUCTIONS.md` para guia detalhado
- Veja `README.md` para documentação completa
