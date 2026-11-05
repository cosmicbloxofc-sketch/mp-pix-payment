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
    const { transaction_id } = req.body;

    // Aqui você implementaria a verificação real no AnubisPay
    // Por enquanto, retorna status pendente
    return res.status(200).json({
      success: true,
      transaction_id: transaction_id || '',
      status: 'PENDING',
      paid: false
    });

  } catch (error) {
    console.error('Erro ao verificar pagamento:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Erro ao verificar pagamento'
    });
  }
}
