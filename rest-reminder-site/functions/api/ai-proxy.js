/**
 * 休息提醒 AI 代理 Pages Function
 * 挂载路径: /api/ai-proxy
 * 隐藏 SenseNova/Agnes API Key，桌面应用通过此 Function 调用 AI
 * 限流：每 IP 每天 30 次
 */

const UPSTREAMS = [
  {
    name: 'SenseNova',
    url: 'https://token.sensenova.cn/v1/chat/completions',
    keyEnv: 'SENSENOVA_KEY',
    model: 'sensenova-6.7-flash-lite',
  },
  {
    name: 'Agnes',
    url: 'https://apihub.agnes-ai.com/v1/chat/completions',
    keyEnv: 'AGNES_KEY',
    model: 'agnes-2.0-flash',
  },
];

const ALLOWED_MODELS = new Set([
  'sensenova-6.7-flash-lite',
  'agnes-2.0-flash',
  'auto',
]);

const RATE_LIMIT = 30;
const rateMap = new Map();

function checkRateLimit(ip) {
  const today = new Date().toISOString().slice(0, 10);
  const entry = rateMap.get(ip);
  if (!entry || entry.date !== today) {
    rateMap.set(ip, { date: today, count: 1 });
    return true;
  }
  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { headers: CORS });
}

export async function onRequestPost(context) {
  const { request, env } = context;

  // 限流
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (!checkRateLimit(ip)) {
    return new Response(JSON.stringify({
      error: { message: '今日调用次数已达上限（30次/天），请明天再试或配置自己的 AI 服务' }
    }), { status: 429, headers: { 'Content-Type': 'application/json', ...CORS } });
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: { message: 'Invalid JSON' } }), {
      status: 400, headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  const requestedModel = body.model || 'auto';
  if (!ALLOWED_MODELS.has(requestedModel)) {
    return new Response(JSON.stringify({
      error: { message: `Model not allowed. Use auto, sensenova-6.7-flash-lite, or agnes-2.0-flash` }
    }), { status: 403, headers: { 'Content-Type': 'application/json', ...CORS } });
  }

  const errors = [];
  for (const upstream of UPSTREAMS) {
    const key = env[upstream.keyEnv];
    if (!key) { errors.push(`${upstream.name}: 未配置 key`); continue; }

    const useModel = requestedModel === 'auto' ? upstream.model : requestedModel;
    const forwardBody = { ...body, model: useModel };

    try {
      const resp = await fetch(upstream.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${key}` },
        body: JSON.stringify(forwardBody),
      });

      if (resp.status === 200) {
        const data = await resp.text();
        return new Response(data, { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } });
      }
      const errText = await resp.text();
      errors.push(`${upstream.name}: HTTP ${resp.status} ${errText.slice(0, 100)}`);
    } catch (e) {
      errors.push(`${upstream.name}: ${e.message}`);
    }
  }

  return new Response(JSON.stringify({
    error: { message: `所有 AI 服务不可用。${errors.join(' | ')}` }
  }), { status: 502, headers: { 'Content-Type': 'application/json', ...CORS } });
}
