/**
 * 休息提醒 AI 代理 Pages Function
 * 挂载路径: /api/ai-proxy
 * 隐藏 SenseNova/Agnes API Key，桌面应用通过此 Function 调用 AI
 * 安全：CORS 白名单 + 客户端 token 鉴权 + 内存限流（30次/天/IP）
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

// CORS 白名单：仅允许官网域名 + 桌面应用（file://）调用
// 桌面应用走 fetch 时 Origin 为 null 或 file://，需放行
const ALLOWED_ORIGINS = new Set([
  'https://crazy-rest-reminder.pages.dev',
  'https://rest-reminder.pages.dev',
  'https://library-remind.pages.dev',
  'http://localhost:3000',
  'null', // 桌面应用 file:// 协议
]);

// 客户端 token：桌面应用硬编码此值，防止任意网站盗用
// env.APP_TOKEN 通过 wrangler secret put 设置；若未配置则放行（兼容旧客户端）
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

function getCorsHeaders(origin) {
  const allowOrigin = ALLOWED_ORIGINS.has(origin) ? origin : 'https://crazy-rest-reminder.pages.dev';
  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-App-Token',
    'Vary': 'Origin',
  };
}

export async function onRequestOptions(context) {
  const { request } = context;
  const origin = request.headers.get('Origin') || '';
  return new Response(null, { headers: getCorsHeaders(origin) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const origin = request.headers.get('Origin') || '';
  const corsHeaders = getCorsHeaders(origin);

  // 鉴权：若 env.APP_TOKEN 已配置，则校验 X-App-Token 头
  const appToken = env.APP_TOKEN;
  if (appToken) {
    const clientToken = request.headers.get('X-App-Token');
    if (clientToken !== appToken) {
      return new Response(JSON.stringify({
        error: { message: '未授权：缺少或错误的 X-App-Token' }
      }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
  }

  // 限流
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (!checkRateLimit(ip)) {
    return new Response(JSON.stringify({
      error: { message: '今日调用次数已达上限（30次/天），请明天再试或配置自己的 AI 服务' }
    }), { status: 429, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: { message: 'Invalid JSON' } }), {
      status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }

  const requestedModel = body.model || 'auto';
  if (!ALLOWED_MODELS.has(requestedModel)) {
    return new Response(JSON.stringify({
      error: { message: `Model not allowed. Use auto, sensenova-6.7-flash-lite, or agnes-2.0-flash` }
    }), { status: 403, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
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
        return new Response(data, { status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
      }
      const errText = await resp.text();
      errors.push(`${upstream.name}: HTTP ${resp.status} ${errText.slice(0, 100)}`);
    } catch (e) {
      errors.push(`${upstream.name}: ${e.message}`);
    }
  }

  return new Response(JSON.stringify({
    error: { message: `所有 AI 服务不可用。${errors.join(' | ')}` }
  }), { status: 502, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
}
