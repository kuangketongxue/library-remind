import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';

function buildOutline(monthKey, signals) {
  return `【${monthKey} 深度访谈大纲】\n1) 本月最有价值的三个决策\n2) 哪些动作带来可量化收益\n3) 哪些阻力反复出现\n4) 下月一小时可执行实验\n\n数据依据:\n${signals}`;
}

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const now = new Date();
  const monthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

  const token = await query(
    `select coalesce(sum(total_tokens),0)::int as total_tokens from token_usage where user_id = $1 and to_char(created_at, 'YYYY-MM') = $2`,
    [user.id, monthKey]
  );

  const diary = await query(
    `select count(*)::int as diary_count from diary_entries where user_id = $1 and to_char(created_at, 'YYYY-MM') = $2`,
    [user.id, monthKey]
  );

  const traits = await query(
    `select trait, count(*)::int as count from trait_logs where user_id = $1 and to_char(created_at, 'YYYY-MM') = $2 group by trait order by count desc limit 3`,
    [user.id, monthKey]
  );

  const traitText = traits.rows.map((x) => `${x.trait}(${x.count})`).join(' / ') || '暂无';
  const signals = `Token总量: ${token.rows[0].total_tokens}; 日记数量: ${diary.rows[0].diary_count}; 高频特质: ${traitText}`;

  const outline = buildOutline(monthKey, signals);
  const report = `本月你最明显的增长轨迹：持续把想法落成可执行步骤。下月建议保持每周一次复盘和一次深访。`;

  const saved = await query(
    `insert into monthly_interviews (user_id, month_key, outline, report, status)
     values ($1, $2, $3, $4, 'ready')
     on conflict (user_id, month_key)
     do update set outline = excluded.outline, report = excluded.report, status = 'ready'
     returning id, month_key, outline, report, status`,
    [user.id, monthKey, outline, report]
  );

  return Response.json({ interview: saved.rows[0] });
}

