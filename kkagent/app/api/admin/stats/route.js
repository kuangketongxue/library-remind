import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function GET(request) {
  const user = await getCurrentUser(request);
  if (!user?.is_admin) return jsonError('仅管理员可访问', 403);

  const token = await query(
    `select
      coalesce(sum(case when created_at::date = now()::date then total_tokens else 0 end), 0)::int as today_total,
      coalesce(sum(total_tokens), 0)::int as all_total
     from token_usage`
  );

  const users = await query('select count(*)::int as count from users');
  const sessions = await query('select count(*)::int as count from sessions');

  return Response.json({
    stats: {
      todayTokens: token.rows[0].today_total,
      allTokens: token.rows[0].all_total,
      users: users.rows[0].count,
      sessions: sessions.rows[0].count
    }
  });
}

