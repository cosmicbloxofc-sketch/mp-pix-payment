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
    const { cpf } = req.body;
    const cpfLimpo = (cpf || '').replace(/\D/g, '');

    if (!cpfLimpo || cpfLimpo.length !== 11) {
      return res.status(400).json({
        success: false,
        error: 'CPF inválido ou não fornecido'
      });
    }

    // Consulta API de CPF
    const response = await fetch(`https://suapendencia.org/atencao1/api.php?cpf=${cpfLimpo}`);
    
    if (!response.ok) {
      return res.status(500).json({
        success: false,
        error: 'Erro ao consultar CPF'
      });
    }

    const data = await response.json();

    return res.status(200).json({
      success: true,
      nome: data.nome || '',
      cpf: data.cpf || cpfLimpo,
      data_nascimento: data.data_nascimento || ''
    });

  } catch (error) {
    console.error('Erro ao processar CPF:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Erro ao processar CPF'
    });
  }
}
