import { cookies } from 'next/headers';
import { authCookieName } from '@/lib/auth';

export async function POST() {
  const cookieStore = await cookies();
  cookieStore.delete(authCookieName);
  return Response.json({ ok: true });
}

