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
    const data = req.body;
    console.log('Webhook recebido:', JSON.stringify(data));

    return res.status(200).json({
      received: true,
      message: 'Webhook recebido com sucesso'
    });

  } catch (error) {
    console.error('Erro no webhook:', error);
    return res.status(200).json({
      received: false,
      error: error.message
    });
  }
}
