import { getCurrentUser, jsonError } from '@/lib/server';
import { query } from '@/lib/db';
import { fastestFreeModel, consensusMode } from '@/lib/ai';
import { createTraitSummary } from '@/lib/traits';
import { estimateTokens } from '@/lib/server';

export async function GET(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const result = await query(
    `select id, role, content, model, feedback, created_at
     from messages
     where session_id = $1 and user_id = $2
     order by created_at asc`,
    [params.id, user.id]
  );

  return Response.json({ messages: result.rows });
}

export async function POST(request, { params }) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const content = String(body.content || '').trim();
  const advanced = Boolean(body.advanced);
  const openrouterKey = String(body.openrouterKey || '').trim() || undefined;
  const nvidiaKey = String(body.nvidiaKey || '').trim() || undefined;

  if (!content) return jsonError('内容不能为空');

  await query(
    `insert into messages (session_id, user_id, role, content, model)
     values ($1, $2, 'user', $3, 'human')`,
    [params.id, user.id, content]
  );

  const history = await query(
    `select role, content from messages
     where session_id = $1 and user_id = $2
     order by created_at asc
     limit 20`,
    [params.id, user.id]
  );

  const ai = advanced
    ? await consensusMode(history.rows, { openrouterKey, nvidiaKey })
    : await fastestFreeModel(history.rows, { openrouterKey, nvidiaKey });

  const assistant = await query(
    `insert into messages (session_id, user_id, role, content, model)
     values ($1, $2, 'assistant', $3, $4)
     returning id, role, content, model, feedback, created_at`,
    [params.id, user.id, ai.text || '暂时没有拿到回复', `${ai.provider}:${ai.model}`]
  );

  await query(
    `update sessions
     set updated_at = now(), title = case when title = '新对话' then left($1, 40) else title end
     where id = $2 and user_id = $3`,
    [content, params.id, user.id]
  );

  const promptTokens = estimateTokens(content);
  const completionTokens = estimateTokens(ai.text || '');
  await query(
    `insert into token_usage (user_id, session_id, message_id, prompt_tokens, completion_tokens, total_tokens, provider, model)
     values ($1, $2, $3, $4, $5, $6, $7, $8)`,
    [
      user.id,
      params.id,
      assistant.rows[0].id,
      promptTokens,
      completionTokens,
      promptTokens + completionTokens,
      ai.provider,
      ai.model
    ]
  );

  const summary = await createTraitSummary({
    userId: user.id,
    sessionId: params.id,
    messageId: assistant.rows[0].id,
    userInstruction: content,
    aiReply: ai.text
  });

  return Response.json({
    assistant: assistant.rows[0],
    summary,
    peerOutputs: ai.peerOutputs || []
  });
}

