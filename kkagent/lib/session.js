import { cookies } from 'next/headers';
import { verifyToken, authCookieName } from '@/lib/auth';
import { query } from '@/lib/db';

export async function getServerUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get(authCookieName)?.value;
  const payload = verifyToken(token);
  if (!payload?.userId) return null;

  const result = await query(
    'select id, email, display_name, is_admin from users where id = $1 limit 1',
    [payload.userId]
  );
  return result.rows[0] || null;
}

