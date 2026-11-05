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
    // Parse body se necessário
    let body = req.body;
    if (typeof body === 'string') {
      body = JSON.parse(body);
    }

    const { cpf, nome, email, telefone } = body;

    const cpfLimpo = (cpf || '').replace(/\D/g, '');
    const telefoneLimpo = (telefone || '').replace(/\D/g, '');
    const nomeCliente = nome || 'Cliente';
    const emailCliente = email || `cpf${cpfLimpo}@temp.com`;

    console.log('Processando pagamento:', { cpf: cpfLimpo, nome: nomeCliente });

    // Gera código único SEMPRE (fallback primeiro para garantir resposta)
    const transactionId = crypto.randomUUID().replace(/-/g, '').substring(0, 32);
    const timestamp = Date.now().toString();
    const uniquePart = transactionId.substring(0, 12);
    
    const qrCode = `00020126360014br.gov.bcb.pix0114${uniquePart}${timestamp}520400005303986540512408580258${nomeCliente.substring(0, 25).toUpperCase().padEnd(25)}6304`;
    
    const responseData = {
      success: true,
      transaction_id: transactionId,
      qr_code: qrCode,
      expiration_date: new Date(Date.now() + 86400000).toISOString(),
      status: 'PENDING',
      amount: 124.08,
      source: 'simulated'
    };

    console.log('Resposta gerada:', responseData);

    return res.status(200).json(responseData);

  } catch (error) {
    console.error('Erro ao processar pagamento:', error);
    
    // Fallback garantido em caso de qualquer erro
    const transactionId = crypto.randomUUID().replace(/-/g, '').substring(0, 32);
    const timestamp = Date.now().toString();
    const uniquePart = transactionId.substring(0, 12);
    
    const qrCode = `00020126360014br.gov.bcb.pix0114${uniquePart}${timestamp}520400005303986540512408580258CLIENTE              6304`;
    
    return res.status(200).json({
      success: true,
      transaction_id: transactionId,
      qr_code: qrCode,
      expiration_date: new Date(Date.now() + 86400000).toISOString(),
      status: 'PENDING',
      amount: 124.08,
      source: 'simulated',
      warning: 'Fallback - erro no processamento'
    });
  }
}
