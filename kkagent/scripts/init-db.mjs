import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });
import { Pool } from 'pg';

const sql = `
create schema if not exists kkagent;
set search_path to kkagent, public;

create extension if not exists pgcrypto;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  password_hash text not null,
  display_name text,
  is_admin boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  title text not null default '新对话',
  pinned boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  role text not null,
  content text not null,
  model text,
  feedback smallint not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists trait_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  session_id uuid not null references sessions(id) on delete cascade,
  message_id uuid references messages(id) on delete set null,
  trait text not null,
  context text not null,
  instruction text,
  source_pointer text not null,
  created_at timestamptz not null default now()
);

create table if not exists diary_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  kind text not null check (kind in ('success', 'money')),
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists announcements (
  id bigserial primary key,
  content text not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists token_usage (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  session_id uuid references sessions(id) on delete set null,
  message_id uuid references messages(id) on delete set null,
  prompt_tokens int not null default 0,
  completion_tokens int not null default 0,
  total_tokens int not null default 0,
  provider text,
  model text,
  created_at timestamptz not null default now()
);

create table if not exists user_settings (
  user_id uuid primary key references users(id) on delete cascade,
  openrouter_key_enc text,
  nvidia_key_enc text,
  advanced_mode boolean not null default false,
  updated_at timestamptz not null default now()
);

create table if not exists monthly_interviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  month_key text not null,
  outline text,
  report text,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  unique(user_id, month_key)
);

create table if not exists sleep_mode_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  day date not null,
  report text not null,
  created_at timestamptz not null default now(),
  unique(user_id, day)
);

create index if not exists idx_sessions_user_updated on sessions(user_id, updated_at desc);
create index if not exists idx_messages_session_created on messages(session_id, created_at asc);
create index if not exists idx_trait_logs_user_created on trait_logs(user_id, created_at desc);
create index if not exists idx_token_usage_user_created on token_usage(user_id, created_at desc);
`;

async function run() {
  const connectionString = process.env.DIRECT_URL || process.env.DATABASE_URL;
  if (!connectionString) {
    console.error('DIRECT_URL or DATABASE_URL is required for db:init');
    process.exit(1);
  }

  const pool = new Pool({
    connectionString,
    options: '-c search_path=kkagent,public',
    ssl: { rejectUnauthorized: false }
  });

  try {
    await pool.query(sql);
    console.log('Database initialized successfully.');
  } finally {
    await pool.end();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});



