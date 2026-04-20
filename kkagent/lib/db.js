import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL || process.env.DIRECT_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL or DIRECT_URL is required.');
}

const globalForPool = globalThis;

export const pool =
  globalForPool.__kkagentPool ||
  new Pool({
    connectionString,
    options: '-c search_path=kkagent,public',
    ssl: { rejectUnauthorized: false }
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPool.__kkagentPool = pool;
}

export async function query(text, params = []) {
  return pool.query(text, params);
}

