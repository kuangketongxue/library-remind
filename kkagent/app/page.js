import { redirect } from 'next/navigation';
import { getServerUser } from '@/lib/session';

export default async function HomePage() {
  const user = await getServerUser();
  if (user) redirect('/dashboard');
  redirect('/login');
}

