import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function POST(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const latest = await query(
    `select id, role, content
     from messages
     where session_id = $1 and user_id = $2 and role = 'assistant'
     order by created_at desc
     limit 1`,
    [params.id, user.id]
  );

  if (!latest.rows[0]) return jsonError('没有可总结的回复', 404);

  const trace = latest.rows[0];
  return Response.json({
    trait: '目标导向沟通',
    context: '手动触发回顾',
    instruction: trace.content.slice(0, 120),
    sourcePointer: `session:${params.id}|message:${trace.id}`
  });
}

