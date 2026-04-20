import { cookies } from 'next/headers';
import { authCookieName, signToken } from '@/lib/auth';
import { query } from '@/lib/db';
import { jsonError } from '@/lib/server';
import { hashPassword } from '@/lib/auth';

export async function POST(request) {
  const body = await request.json();
  const email = String(body.email || '').trim().toLowerCase();
  const password = String(body.password || '');
  const displayName = String(body.displayName || '').trim();

  if (!email || !password) return jsonError('邮箱和密码不能为空');
  if (password.length < 6) return jsonError('密码至少 6 位');

  const exists = await query('select id from users where email = $1 limit 1', [email]);
  if (exists.rows.length) return jsonError('该邮箱已注册', 409);

  const countResult = await query('select count(*)::int as count from users');
  const userCount = countResult.rows[0]?.count || 0;
  const isAdmin = userCount === 0;

  const passwordHash = await hashPassword(password);
  const inserted = await query(
    `insert into users (email, password_hash, display_name, is_admin)
     values ($1, $2, $3, $4)
     returning id, email, display_name, is_admin`,
    [email, passwordHash, displayName || email.split('@')[0], isAdmin]
  );

  const user = inserted.rows[0];
  const token = signToken({ userId: user.id, email: user.email, isAdmin: user.is_admin });

  const cookieStore = await cookies();
  cookieStore.set(authCookieName, token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 7
  });

  return Response.json({ user });
}

