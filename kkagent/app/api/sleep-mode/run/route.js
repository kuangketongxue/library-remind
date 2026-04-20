import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const rows = await query(
    `select role, content, created_at from messages
     where user_id = $1 and created_at::date = now()::date
     order by created_at asc`,
    [user.id]
  );

  const count = rows.rows.length;
  const sample = rows.rows.slice(-6).map((r) => `${r.role}: ${r.content.slice(0, 120)}`).join('\n');

  const report = `今日共 ${count} 条对话。\n关键片段:\n${sample || '暂无数据'}\n\n建议：明日优先延续今天最有产出的主题。`;

  const saved = await query(
    `insert into sleep_mode_reports (user_id, day, report)
     values ($1, now()::date, $2)
     on conflict (user_id, day)
     do update set report = excluded.report, created_at = now()
     returning id, day, report, created_at`,
    [user.id, report]
  );

  return Response.json({ report: saved.rows[0] });
}

