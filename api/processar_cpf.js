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
    // Parse body (pode vir como string ou objeto)
    let cpf;
    
    if (typeof req.body === 'string') {
      // Parse URL encoded
      const params = new URLSearchParams(req.body);
      cpf = params.get('cpf');
    } else {
      cpf = req.body.cpf;
    }

    const cpfLimpo = (cpf || '').replace(/\D/g, '');

    console.log('Consultando CPF:', cpfLimpo);

    if (!cpfLimpo || cpfLimpo.length !== 11) {
      return res.status(400).json({
        success: false,
        error: 'CPF inválido ou não fornecido'
      });
    }

    // Consulta API de CPF (com timeout de 8s)
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const response = await fetch(`https://suapendencia.org/atencao1/api.php?cpf=${cpfLimpo}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      signal: controller.signal
    });
    clearTimeout(timer);
    
    console.log('Response status:', response.status);

    if (!response.ok) {
      console.error('Erro na API de CPF:', response.status);
      return res.status(500).json({
        success: false,
        error: 'Erro ao consultar CPF'
      });
    }

    const data = await response.json();
    console.log('Dados recebidos:', JSON.stringify(data));

    // API externa retorna aninhado em "dados": { status, message, dados: { cpf, nome, ... } }
    const dados = data.dados || data;

    const nome = dados.nome || data.nome || '';
    const nascimento = dados.data_nascimento || data.data_nascimento || '';

    if (!nome) {
      return res.status(200).json({
        success: false,
        error: 'CPF não encontrado.'
      });
    }

    return res.status(200).json({
      success: true,
      nome: nome,
      cpf: dados.cpf || data.cpf || cpfLimpo,
      data_nascimento: nascimento,
      nascimento: nascimento
    });

  } catch (error) {
    console.error('Erro ao processar CPF:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Erro ao processar CPF'
    });
  }
}
