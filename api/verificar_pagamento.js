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
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const body = parseBody(req);
  const url = new URL(req.url || '/', 'http://localhost');
  const transactionId = body.transaction_id || url.searchParams.get('transaction_id');

  if (!transactionId) {
    return res.status(400).json({ success: false, error: 'transaction_id não fornecido' });
  }

  const { pub, sec } = getCredentials();
  const auth = Buffer.from(`${pub}:${sec}`).toString('base64');

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);

  try {
    const response = await fetch(`${ANUBIS_BASE}/v1/payment-transaction/info/${encodeURIComponent(transactionId)}`, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Accept': 'application/json'
      },
      signal: controller.signal
    });
    clearTimeout(timer);

    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = null; }

    // Rate limit da AnubisPay: mantém PENDING e tenta de novo depois
    if (response.status === 429) {
      return res.status(200).json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false });
    }

    if (data && data.success && data.data) {
      const status = data.data.status || 'PENDING';
      return res.status(200).json({
        success: true,
        transaction_id: transactionId,
        status,
        paid: status === 'PAID'
      });
    }

    return res.status(200).json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false });
  } catch (error) {
    clearTimeout(timer);
    return res.status(200).json({ success: true, transaction_id: transactionId, status: 'PENDING', paid: false, warning: error.message });
  }
}
