/**
 * 休息提醒 AI 代理 Worker
 * 隐藏 SenseNova/Agnes API Key，桌面应用通过此 Worker 调用 AI
 * 限流：每 IP 每天 30 次（防止滥用）
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

// 允许的 model 白名单（防止滥用调用昂贵模型）
const ALLOWED_MODELS = new Set([
  'sensenova-6.7-flash-lite',
  'agnes-2.0-flash',
  'auto', // 客户端传 auto 时，Worker 自动选择
]);

// 简单内存限流（每个 Worker 实例独立，近似限流）
const RATE_LIMIT = 30; // 每 IP 每天最多 30 次
const rateMap = new Map(); // ip -> { date, count }

function checkRateLimit(ip) {
  const today = new Date().toISOString().slice(0, 10);
  const entry = rateMap.get(ip);
  if (!entry || entry.date !== today) {
    rateMap.set(ip, { date: today, count: 1 });
    return true;
  }
  if (entry.count >= RATE_LIMIT) {
    return false;
  }
  entry.count++;
  return true;
}

function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

export default {
  async fetch(request, env) {
    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: getCorsHeaders() });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method Not Allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
      });
    }

    // 限流
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (!checkRateLimit(ip)) {
      return new Response(JSON.stringify({
        error: { message: '今日调用次数已达上限（30次/天），请明天再试或配置自己的 AI 服务' }
      }), {
        status: 429,
        headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
      });
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: { message: 'Invalid JSON body' } }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
      });
    }

    // model 校验
    const requestedModel = body.model || 'auto';
    if (!ALLOWED_MODELS.has(requestedModel)) {
      return new Response(JSON.stringify({
        error: { message: `Model ${requestedModel} not allowed. Use auto, sensenova-6.7-flash-lite, or agnes-2.0-flash` }
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
      });
    }

    // 依次尝试上游
    const errors = [];
    for (const upstream of UPSTREAMS) {
      const key = env[upstream.keyEnv];
      if (!key) {
        errors.push(`${upstream.name}: 未配置 key`);
        continue;
      }

      // 自动选择 model
      const useModel = requestedModel === 'auto' ? upstream.model : requestedModel;
      const forwardBody = { ...body, model: useModel };

      try {
        const resp = await fetch(upstream.url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${key}`,
          },
          body: JSON.stringify(forwardBody),
        });

        if (resp.status === 200) {
          const data = await resp.text();
          return new Response(data, {
            status: 200,
            headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
          });
        }

        // 业务错误，尝试下一个上游
        const errText = await resp.text();
        errors.push(`${upstream.name}: HTTP ${resp.status} ${errText.slice(0, 100)}`);
      } catch (e) {
        errors.push(`${upstream.name}: ${e.message}`);
      }
    }

    // 所有上游都失败
    return new Response(JSON.stringify({
      error: { message: `所有 AI 服务不可用。${errors.join(' | ')}` }
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', ...getCorsHeaders() },
    });
  },
};
