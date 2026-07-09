/**
 * 邮件发送代理 — Cloudflare Pages Function
 * 挂载路径: /api/send-email
 * 通过 Resend API 发送邮件（Cloudflare 兼容的邮件服务）
 *
 * 环境变量（wrangler secret put）：
 *   RESEND_API_KEY — Resend API Key（https://resend.com）
 *   EMAIL_FROM     — 发件人地址（需验证域名）
 *
 * 客户端调用：POST /api/send-email
 * Body: { to, subject, html }
 */

const ALLOWED_ORIGINS = new Set([
  'chrome-extension://',
  'https://crazy-rest-reminder.pages.dev',
  'null',
]);

function getCorsHeaders(origin) {
  const allowOrigin = origin?.startsWith('chrome-extension://') || ALLOWED_ORIGINS.has(origin)
    ? (origin || '*') : 'https://crazy-rest-reminder.pages.dev';
  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

export async function onRequestOptions(context) {
  const origin = context.request.headers.get('Origin') || '';
  return new Response(null, { headers: getCorsHeaders(origin) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const origin = request.headers.get('Origin') || '';
  const corsHeaders = getCorsHeaders(origin);

  let body;
  try { body = await request.json(); } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }

  const { to, subject, html } = body;
  if (!to || !subject || !html) {
    return new Response(JSON.stringify({ error: '缺少 to/subject/html' }), {
      status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }

  const apiKey = env.RESEND_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: '邮件服务未配置' }), {
      status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }

  try {
    const resp = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: env.EMAIL_FROM || 'rest-reminder@crazy-rest-reminder.pages.dev',
        to: [to],
        subject,
        html,
      }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.message || `HTTP ${resp.status}`);
    return new Response(JSON.stringify({ ok: true, id: data.id }), {
      status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }
}
