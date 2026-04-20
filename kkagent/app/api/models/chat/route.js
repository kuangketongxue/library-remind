import { getCurrentUser, jsonError } from '@/lib/server';
import { fastestFreeModel, consensusMode, getModelCatalog } from '@/lib/ai';

export async function POST(request) {
  const user = await getCurrentUser(request);
  if (!user) return jsonError('未登录', 401);

  const body = await request.json();
  const content = String(body.content || '').trim();
  const advanced = Boolean(body.advanced);
  const openrouterKey = String(body.openrouterKey || '').trim() || undefined;
  const nvidiaKey = String(body.nvidiaKey || '').trim() || undefined;

  if (!content) return jsonError('请输入内容');

  const messages = [{ role: 'user', content }];
  const result = advanced
    ? await consensusMode(messages, { openrouterKey, nvidiaKey })
    : await fastestFreeModel(messages, { openrouterKey, nvidiaKey });

  return Response.json({
    result,
    catalog: getModelCatalog()
  });
}

