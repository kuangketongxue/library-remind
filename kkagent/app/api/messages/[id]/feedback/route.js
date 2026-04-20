import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function PATCH(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const feedback = Number(body.feedback) || 0;
  if (![1, -1, 0].includes(feedback)) return jsonError('反馈值无效');

  const updated = await query(
    `update messages
     set feedback = $1
     where id = $2 and user_id = $3 and role = 'assistant'
     returning id, feedback`,
    [feedback, params.id, user.id]
  );

  return Response.json({ message: updated.rows[0] || null });
}

