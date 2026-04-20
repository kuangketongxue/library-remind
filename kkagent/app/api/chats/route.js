import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function GET(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const search = new URL(request.url).searchParams.get('q')?.trim().toLowerCase();

  const result = await query(
    `select id, title, pinned, created_at, updated_at
     from sessions
     where user_id = $1
     and ($2::text is null or lower(title) like '%' || $2 || '%')
     order by pinned desc, updated_at desc`,
    [user.id, search || null]
  );

  return Response.json({ sessions: result.rows });
}

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const title = String(body.title || '新对话').slice(0, 80);

  const result = await query(
    `insert into sessions (user_id, title)
     values ($1, $2)
     returning id, title, pinned, created_at, updated_at`,
    [user.id, title]
  );

  return Response.json({ session: result.rows[0] });
}

