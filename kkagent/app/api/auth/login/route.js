import { cookies } from 'next/headers';
import { authCookieName, comparePassword, signToken } from '@/lib/auth';
import { query } from '@/lib/db';
import { jsonError } from '@/lib/server';

export async function POST(request) {
  const body = await request.json();
  const email = String(body.email || '').trim().toLowerCase();
  const password = String(body.password || '');

  if (!email || !password) return jsonError('邮箱和密码不能为空');

  const result = await query(
    'select id, email, password_hash, display_name, is_admin from users where email = $1 limit 1',
    [email]
  );

  const user = result.rows[0];
  if (!user) return jsonError('账号不存在', 404);

  const valid = await comparePassword(password, user.password_hash);
  if (!valid) return jsonError('密码不正确', 401);

  const token = signToken({ userId: user.id, email: user.email, isAdmin: user.is_admin });
  const cookieStore = await cookies();
  cookieStore.set(authCookieName, token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 7
  });

  return Response.json({
    user: {
      id: user.id,
      email: user.email,
      display_name: user.display_name,
      is_admin: user.is_admin
    }
  });
}

