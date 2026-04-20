import { redirect } from 'next/navigation';
import { getServerUser } from '@/lib/session';
import { query } from '@/lib/db';
import DashboardApp from '@/components/dashboard-app';

export default async function DashboardPage() {
  const user = await getServerUser();
  if (!user) redirect('/login');

  const sessions = await query(
    `select id, title, pinned, created_at, updated_at
     from sessions
     where user_id = $1
     order by pinned desc, updated_at desc`,
    [user.id]
  );

  const firstSessionId = sessions.rows[0]?.id;
  let messages = [];
  if (firstSessionId) {
    const list = await query(
      `select id, role, content, model, feedback, created_at
       from messages
       where session_id = $1 and user_id = $2
       order by created_at asc`,
      [firstSessionId, user.id]
    );
    messages = list.rows;
  }

  const diary = await query(
    `select id, kind, content, created_at
     from diary_entries
     where user_id = $1
     order by created_at desc
     limit 20`,
    [user.id]
  );

  const traits = await query(
    `select id, trait, context, instruction, source_pointer, created_at
     from trait_logs
     where user_id = $1
     order by created_at desc
     limit 20`,
    [user.id]
  );

  const token = await query(
    `select
      coalesce(sum(case when created_at::date = now()::date then total_tokens else 0 end), 0)::int as today_total,
      coalesce(sum(total_tokens), 0)::int as all_total
     from token_usage
     where user_id = $1`,
    [user.id]
  );

  const notice = await query(
    `select id, content, active, created_at
     from announcements
     where active = true
     order by created_at desc
     limit 1`
  );

  return (
    <DashboardApp
      user={user}
      initialSessions={sessions.rows}
      initialMessages={messages}
      initialSessionId={firstSessionId || null}
      initialDiaries={diary.rows}
      initialTraits={traits.rows}
      initialToken={token.rows[0]}
      initialAnnouncement={notice.rows[0] || null}
    />
  );
}

