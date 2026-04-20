import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function GET(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const row = await query(
    `select id, content, active, created_at
     from announcements
     where active = true
     order by created_at desc
     limit 1`
  );

  return Response.json({ announcement: row.rows[0] || null });
}

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user?.is_admin) return jsonError('仅管理员可发布公告', 403);

  const body = await request.json();
  const content = String(body.content || '').trim();
  if (!content) return jsonError('公告不能为空');

  await query('update announcements set active = false where active = true');

  const inserted = await query(
    `insert into announcements (content, active)
     values ($1, true)
     returning id, content, active, created_at`,
    [content]
  );

  return Response.json({ announcement: inserted.rows[0] });
}

