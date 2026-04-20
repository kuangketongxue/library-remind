import { authCookieName, verifyToken } from '@/lib/auth';
import { query } from '@/lib/db';

export function jsonError(message, status = 400) {
  return Response.json({ error: message }, { status });
}

export async function getCurrentUser(request) {
  const token = request.cookies.get(authCookieName)?.value;
  const payload = verifyToken(token);
  if (!payload?.userId) return null;

  const result = await query(
    'select id, email, display_name, is_admin from users where id = $1 limit 1',
    [payload.userId]
  );

  return result.rows[0] || null;
}

export function estimateTokens(text = '') {
  return Math.max(1, Math.ceil(text.length / 4));
}

export function formatPointer({ sessionId, messageId }) {
  return `session:${sessionId}|message:${messageId}`;
}

