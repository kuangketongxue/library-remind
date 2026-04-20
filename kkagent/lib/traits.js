import { query } from '@/lib/db';
import { formatPointer } from '@/lib/server';

function pickTrait(userText = '', aiText = '') {
  if (/计划|plan|roadmap|步骤|拆解/i.test(userText)) return '结构化执行倾向';
  if (/复盘|总结|review|反思/i.test(userText)) return '复盘驱动成长';
  if (/效率|自动化|workflow|system/i.test(userText)) return '系统化效率偏好';
  if ((aiText || '').length > 500) return '偏好深度内容';
  return '目标导向沟通';
}

export async function createTraitSummary({ userId, sessionId, messageId, userInstruction, aiReply }) {
  const trait = pickTrait(userInstruction, aiReply);
  const context = '对话回合结束后的静默总结';
  const sourcePointer = formatPointer({ sessionId, messageId });

  await query(
    `insert into trait_logs (user_id, session_id, message_id, trait, context, instruction, source_pointer)
     values ($1, $2, $3, $4, $5, $6, $7)`,
    [userId, sessionId, messageId, trait, context, userInstruction?.slice(0, 400), sourcePointer]
  );

  return { trait, context, sourcePointer };
}

