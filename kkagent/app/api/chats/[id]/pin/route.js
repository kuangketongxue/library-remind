import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

export async function PATCH(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const pinned = Boolean(body.pinned);

  const result = await query(
    `update sessions
     set pinned = $1, updated_at = now()
     where id = $2 and user_id = $3
     returning id, pinned`,
    [pinned, params.id, user.id]
  );

  return Response.json({ session: result.rows[0] || null });
}

