const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';
const NVIDIA_URL = 'https://integrate.api.nvidia.com/v1/chat/completions';

const DEFAULT_MODEL = 'openroute/free';
const NVIDIA_MODELS = [
  'moonshotai/kimi-k2.5',
  'google/gemma-4-31b-it',
  'z-ai/glm5',
  'qwen3.5-122b-a10b',
  'minimaxai/minimax-m2.7'
];

function timeoutFetch(url, options, timeoutMs = 18000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  return fetch(url, {
    ...options,
    signal: controller.signal
  }).finally(() => clearTimeout(timeout));
}

async function callOpenRouter(messages, model = DEFAULT_MODEL, keyOverride) {
  const key = keyOverride || process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('OPENROUTER_API_KEY is missing');

  const response = await timeoutFetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model, messages, temperature: 0.5 })
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`OpenRouter failed: ${errText}`);
  }

  const data = await response.json();
  return {
    provider: 'openrouter',
    model,
    text: data?.choices?.[0]?.message?.content || ''
  };
}

async function callNvidia(messages, model, keyOverride) {
  const key = keyOverride || process.env.NVIDIA_API_KEY;
  if (!key) throw new Error('NVIDIA_API_KEY is missing');

  const response = await timeoutFetch(NVIDIA_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model, messages, temperature: 0.45 })
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`NVIDIA failed: ${errText}`);
  }

  const data = await response.json();
  return {
    provider: 'nvidia',
    model,
    text: data?.choices?.[0]?.message?.content || ''
  };
}

export function getModelCatalog() {
  return {
    defaultModel: DEFAULT_MODEL,
    nvidiaModels: NVIDIA_MODELS
  };
}

export async function fastestFreeModel(messages, keyOverrides = {}) {
  const tasks = [
    callOpenRouter(messages, DEFAULT_MODEL, keyOverrides.openrouterKey),
    ...NVIDIA_MODELS.map((model) => callNvidia(messages, model, keyOverrides.nvidiaKey))
  ];

  try {
    const result = await Promise.any(tasks);
    if (result?.text) return result;
  } catch {
    // ignore
  }

  return {
    provider: 'fallback',
    model: 'offline-fallback',
    text: '我现在离线，先把你的问题记录好了。请稍后重试，我会补上完整回复。'
  };
}

function voteBest(outputs) {
  const scored = outputs
    .filter((x) => x.text)
    .map((item) => {
      const lengthScore = Math.min(200, item.text.length) / 10;
      const structureBonus = /1\.|2\.|3\.|-/.test(item.text) ? 12 : 0;
      return {
        ...item,
        score: lengthScore + structureBonus
      };
    })
    .sort((a, b) => b.score - a.score);

  return scored[0] || outputs[0];
}

export async function consensusMode(messages, keyOverrides = {}) {
  const tasks = [
    callOpenRouter(messages, DEFAULT_MODEL, keyOverrides.openrouterKey).catch(() => null),
    ...NVIDIA_MODELS.map((m) =>
      callNvidia(messages, m, keyOverrides.nvidiaKey).catch(() => null)
    )
  ];

  const results = (await Promise.all(tasks)).filter(Boolean);

  if (!results.length) {
    return {
      provider: 'fallback',
      model: 'consensus-fallback',
      text: '高级模式暂时不可用，先记录你的问题并建议稍后重试。',
      peerOutputs: []
    };
  }

  const winner = voteBest(results);

  return {
    provider: 'consensus',
    model: winner.model,
    text: winner.text,
    peerOutputs: results.map((x) => ({ model: x.model, preview: x.text.slice(0, 120) }))
  };
}

