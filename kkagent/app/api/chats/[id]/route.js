import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function DELETE(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  await query('delete from sessions where id = $1 and user_id = $2', [params.id, user.id]);
  return Response.json({ ok: true });
}

