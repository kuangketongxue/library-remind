import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function GET(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const rows = await query(
    `select id, kind, content, created_at
     from diary_entries
     where user_id = $1
     order by created_at desc
     limit 100`,
    [user.id]
  );

  return Response.json({ diaries: rows.rows });
}

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const kind = body.kind === 'money' ? 'money' : 'success';
  const content = String(body.content || '').trim();
  if (!content) return jsonError('内容不能为空');

  const inserted = await query(
    `insert into diary_entries (user_id, kind, content)
     values ($1, $2, $3)
     returning id, kind, content, created_at`,
    [user.id, kind, content]
  );

  return Response.json({ diary: inserted.rows[0] });
}

