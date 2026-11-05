# 🚀 Instruções de Deploy na Vercel

## Configuração de Variáveis de Ambiente

As credenciais do AnubisPay devem ser configuradas como variáveis de ambiente na Vercel:

### 1. Acesse o Dashboard da Vercel
- Vá para: https://vercel.com/dashboard
- Selecione o projeto: `mp-pix-payment`

### 2. Configure as Environment Variables
- Clique em **Settings** → **Environment Variables**
- Adicione as seguintes variáveis:

```
ANUBISPAY_PUBLIC_KEY = anubispay_live_[SUA_CHAVE_PUBLICA]
ANUBISPAY_SECRET_KEY = sk_live_[SUA_CHAVE_SECRETA]
```

> **Nota**: As chaves reais devem ser obtidas no dashboard do AnubisPay e configuradas diretamente na Vercel.

### 3. Environments
Marque as variáveis para todos os ambientes:
- ✅ Production
- ✅ Preview
- ✅ Development

### 4. Redeploy
Após adicionar as variáveis, faça redeploy:
- Clique em **Deployments**
- No último deployment, clique nos 3 pontos
- Selecione **Redeploy**

## 📡 Endpoints da API

Após o deploy, os seguintes endpoints estarão disponíveis:

- `POST /processar_pagamento.php` → Gera transação PIX única
- `POST /processar_cpf.php` → Busca dados do CPF
- `POST /verificar_pagamento.php` → Verifica status do pagamento
- `POST /webhook.php` → Recebe webhooks do AnubisPay

## 🌐 URLs

- **Produção**: https://mp-pix-payment.vercel.app/
- **Página de Entrada**: https://mp-pix-payment.vercel.app/confirmar.php
- **Repositório GitHub**: https://github.com/cosmicbloxofc-sketch/mp-pix-payment

## ✅ Checklist de Deploy

- [ ] Fork ou importar repositório na Vercel
- [ ] Configurar variáveis de ambiente (ANUBISPAY_PUBLIC_KEY e ANUBISPAY_SECRET_KEY)
- [ ] Fazer deploy
- [ ] Testar endpoint: `/processar_cpf.php`
- [ ] Testar endpoint: `/processar_pagamento.php`
- [ ] Testar fluxo completo no navegador
- [ ] Verificar geração de códigos PIX únicos

## 🔧 Deploy via CLI (Alternativa)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd /tmp/mp-local
vercel --prod

# Configurar secrets
vercel env add ANUBISPAY_PUBLIC_KEY
# Cole sua chave pública do AnubisPay

vercel env add ANUBISPAY_SECRET_KEY
# Cole sua chave secreta do AnubisPay

# Redeploy com as novas variáveis
vercel --prod
```

## 🎯 Domínio Personalizado (Opcional)

Para configurar o domínio personalizado:
1. Vá em **Settings** → **Domains**
2. Adicione: `mp-pix-payment.vercel.app` (já configurado automaticamente)
3. Ou adicione seu domínio customizado

## 📝 Notas Importantes

⚠️ **Segurança**: Nunca commite as chaves reais no Git. Use sempre variáveis de ambiente.

✅ **Fallback**: O sistema possui fallback automático que gera códigos simulados únicos caso a API AnubisPay falhe.

🔄 **Atualização**: Qualquer push para a branch `main` do GitHub irá automaticamente fazer redeploy na Vercel (se configurado).

## 🐛 Troubleshooting

### API não responde
- Verifique se as variáveis de ambiente estão configuradas
- Confira os logs em: Vercel Dashboard → Deployments → [seu deploy] → Runtime Logs

### Erro 500 nas APIs
- Verifique se o `requirements.txt` tem todas as dependências
- Confira os logs para ver erro específico

### CORS Error
- Todas as APIs serverless já possuem CORS habilitado
- Verifique se está usando os endpoints corretos

## ✨ Sucesso!

Após configurar tudo, acesse:
**https://mp-pix-payment.vercel.app/confirmar.php**

E teste o fluxo completo de pagamento PIX!
