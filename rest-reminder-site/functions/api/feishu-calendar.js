/**
 * 飞书日历代理 — Cloudflare Pages Function
 * 挂载路径: /api/feishu-calendar
 * 通过飞书开放 API 获取日程，替代桌面版的 lark-cli
 *
 * 环境变量（wrangler secret put）：
 *   FEISHU_APP_ID     — 飞书自建应用 App ID
 *   FEISHU_APP_SECRET — 飞书自建应用 App Secret
 *
 * 客户端调用：GET /api/feishu-calendar?start=2026-07-10&end=2026-07-11
 */

const ALLOWED_ORIGINS = new Set([
  'chrome-extension://',  // Chrome 扩展（origin 为 chrome-extension://id）
  'https://crazy-rest-reminder.pages.dev',
  'null',
]);

function getCorsHeaders(origin) {
  const allowOrigin = ALLOWED_ORIGINS.has(origin) || origin?.startsWith('chrome-extension://')
    ? (origin || '*') : 'https://crazy-rest-reminder.pages.dev';
  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

// tenant_access_token 缓存（内存级，Worker 冷启动后重建）
let tokenCache = { token: '', expiresAt: 0 };

async function getTenantToken(env) {
  if (tokenCache.token && Date.now() < tokenCache.expiresAt) return tokenCache.token;

  const resp = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: env.FEISHU_APP_ID, app_secret: env.FEISHU_APP_SECRET }),
  });
  const data = await resp.json();
  if (data.code !== 0) throw new Error(`飞书认证失败: ${data.msg}`);
  tokenCache = { token: data.tenant_access_token, expiresAt: Date.now() + (data.expire - 300) * 1000 };
  return tokenCache.token;
}

export async function onRequestOptions(context) {
  const origin = context.request.headers.get('Origin') || '';
  return new Response(null, { headers: getCorsHeaders(origin) });
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const origin = request.headers.get('Origin') || '';
  const corsHeaders = getCorsHeaders(origin);

  try {
    const url = new URL(request.url);
    const start = url.searchParams.get('start') || new Date().toISOString().slice(0, 10);
    const end = url.searchParams.get('end') || start;

    const token = await getTenantToken(env);

    // 获取用户日程（需要 user_access_token 或用 tenant_token 查日历）
    // 简化：用日历事件 API
    const calResp = await fetch(
      `https://open.feishu.cn/open-apis/calendar/v4/calendars/primary/events?start_time=${start}T00:00:00&end_time=${end}T23:59:59&page_size=50`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    const calData = await calResp.json();

    if (calData.code !== 0) {
      return new Response(JSON.stringify({ error: calData.msg, events: [] }), {
        status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    const events = (calData.data?.items || []).map(e => ({
      summary: e.summary || '(无标题)',
      start: e.start_time?.date || e.start_time?.timestamp,
      end: e.end_time?.date || e.end_time?.timestamp,
      status: e.status,
    }));

    return new Response(JSON.stringify({ events, count: events.length }), {
      status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message, events: [] }), {
      status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }
}
