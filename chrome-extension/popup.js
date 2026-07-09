// ═══ 精力管理 — Popup 逻辑 ═══

const FOCUS_SECONDS = 60 * 60;
const REST_SECONDS = 5 * 60;
const DAILY_LIMIT_HOUR = 22;

const AMBIENT_SOUNDS = [
  { id: 'rain', icon: '🌧️', name: '雨声' },
  { id: 'forest', icon: '🌲', name: '森林' },
  { id: 'cafe', icon: '☕', name: '咖啡馆' },
  { id: 'white', icon: '📻', name: '白噪音' },
  { id: 'brown', icon: '🌊', name: '棕色噪音' },
];

let currentState = null;
let tickInterval = null;
let ambientCtx = null;
let onboardStep = 0;

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', async () => {
  // 检查是否首次使用
  const res = await chrome.storage.local.get(['onboarded', 'settings']);
  if (!res.onboarded) {
    showOnboarding();
  }

  // 主题
  const theme = res.settings?.theme || 'dark';
  applyTheme(theme);

  chrome.runtime.sendMessage({ action: 'getState' }, (state) => {
    currentState = state;
    render();
    startTick();

    // streak
    if (state.streak > 0) {
      document.getElementById('streakBar').style.display = 'block';
      document.getElementById('streakCount').textContent = state.streak;
    }
  });

  document.getElementById('mainBtn').addEventListener('click', onMainBtnClick);
  document.getElementById('skipBtn').addEventListener('click', onSkip);
  document.getElementById('optionsLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });

  // 主题切换
  document.getElementById('themeToggle').addEventListener('click', (e) => {
    e.preventDefault();
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    chrome.storage.local.get(['settings'], (r) => {
      const s = r.settings || {};
      s.theme = next;
      chrome.storage.local.set({ settings: s });
    });
  });

  // 快捷入口
  document.querySelectorAll('.shortcut').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      chrome.tabs.create({ url: chrome.runtime.getURL(el.dataset.page) });
    });
  });

  renderAmbientBtns();
});

// ── 首次引导 ──
function showOnboarding() {
  document.getElementById('onboarding').style.display = 'flex';
  onboardStep = 0;
  updateOnboardStep();

  document.getElementById('onboardNext').addEventListener('click', () => {
    onboardStep++;
    if (onboardStep >= 3) {
      document.getElementById('onboarding').style.display = 'none';
      chrome.storage.local.set({ onboarded: true });
      return;
    }
    updateOnboardStep();
  });
}

function updateOnboardStep() {
  document.querySelectorAll('.onboard-step').forEach((el, i) => {
    el.style.display = i === onboardStep ? 'block' : 'none';
  });
  document.querySelectorAll('.dot').forEach((d, i) => {
    d.classList.toggle('active', i === onboardStep);
  });
  document.getElementById('onboardNext').textContent = onboardStep >= 2 ? '开始使用' : '下一步';
}

// ── 主题 ──
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const toggle = document.getElementById('themeToggle');
  if (toggle) toggle.textContent = theme === 'dark' ? '🌙' : '☀️';
}

// ── 白噪音 ──
function renderAmbientBtns() {
  const container = document.getElementById('ambientBtns');
  container.innerHTML = AMBIENT_SOUNDS.map(s =>
    `<button class="ambient-btn" data-sound="${s.id}" title="${s.name}">${s.icon}</button>`
  ).join('');

  container.querySelectorAll('.ambient-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const sound = btn.dataset.sound;
      if (currentState.ambientSound === sound) {
        stopAmbient();
        btn.classList.remove('active');
      } else {
        playAmbient(sound);
        container.querySelectorAll('.ambient-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
    });
  });
}

function playAmbient(type) {
  stopAmbient();
  try {
    ambientCtx = new AudioContext();
    const gain = ambientCtx.createGain();
    gain.gain.value = 0.3;
    const bufferSize = 2 * ambientCtx.sampleRate;
    const buffer = ambientCtx.createBuffer(1, bufferSize, ambientCtx.sampleRate);
    const data = buffer.getChannelData(0);

    if (type === 'white') {
      for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    } else if (type === 'brown') {
      let last = 0;
      for (let i = 0; i < bufferSize; i++) {
        const w = Math.random() * 2 - 1;
        data[i] = (last + 0.02 * w) / 1.02; last = data[i]; data[i] *= 3.5;
      }
    } else if (type === 'rain') {
      for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1) * (0.5 + 0.5 * Math.sin(i / 1000));
    } else {
      let last = 0;
      for (let i = 0; i < bufferSize; i++) {
        const w = Math.random() * 2 - 1;
        data[i] = (last + 0.01 * w) / 1.01; last = data[i]; data[i] *= 2;
      }
    }

    const source = ambientCtx.createBufferSource();
    source.buffer = buffer; source.loop = true;
    source.connect(gain).connect(ambientCtx.destination);
    source.start();
    currentState.ambientSound = type;
    chrome.runtime.sendMessage({ action: 'playAmbient', sound: type });
  } catch (e) { console.error('Audio failed:', e); }
}

function stopAmbient() {
  if (ambientCtx) { ambientCtx.close().catch(() => {}); ambientCtx = null; }
  currentState.ambientSound = '';
  chrome.runtime.sendMessage({ action: 'stopAmbient' });
}

// ── 渲染 ──
function render() {
  if (!currentState) return;
  const { timerState } = currentState;

  const badge = document.getElementById('statusBadge');
  badge.className = `status-badge ${timerState}`;
  const stateNames = { idle: '待机', running: '学习中', paused: '已暂停', resting: '休息中', review: '复盘中' };
  badge.textContent = stateNames[timerState] || timerState;

  const display = document.getElementById('timerDisplay');
  display.className = `timer-display ${timerState}`;
  display.textContent = formatTime(getRemaining());

  const subtitle = document.getElementById('subtitle');
  const subtitles = {
    idle: '点击开始学习', running: '保持专注 💪', paused: '已暂停，点击继续',
    resting: '休息一下 ☕', review: '请为本轮评分',
  };
  subtitle.textContent = subtitles[timerState] || '';

  const mainBtn = document.getElementById('mainBtn');
  const skipBtn = document.getElementById('skipBtn');
  mainBtn.style.background = ''; mainBtn.style.color = '';
  mainBtn.disabled = false; mainBtn.onclick = onMainBtnClick;

  if (timerState === 'idle') {
    const hour = currentState.hour || new Date().getHours();
    if (hour >= DAILY_LIMIT_HOUR) {
      mainBtn.textContent = `⏰ ${DAILY_LIMIT_HOUR}:00 后休息`;
      mainBtn.className = 'btn btn-secondary'; mainBtn.disabled = true;
    } else {
      mainBtn.textContent = '▶ 开始学习';
      mainBtn.className = 'btn btn-primary';
    }
    skipBtn.style.display = 'none';
  } else if (timerState === 'running') {
    mainBtn.textContent = '⏸ 暂停'; mainBtn.className = 'btn btn-primary';
    mainBtn.style.background = 'var(--danger)'; mainBtn.style.color = '#fff';
    skipBtn.style.display = 'block';
  } else if (timerState === 'paused') {
    mainBtn.textContent = '▶ 继续'; mainBtn.className = 'btn btn-primary';
    skipBtn.style.display = 'none';
  } else if (timerState === 'resting') {
    mainBtn.textContent = '☕ 休息中...'; mainBtn.className = 'btn btn-secondary';
    mainBtn.disabled = true; skipBtn.style.display = 'none';
  } else if (timerState === 'review') {
    mainBtn.textContent = '📝 去复盘'; mainBtn.className = 'btn btn-primary';
    mainBtn.style.background = 'var(--accent)'; mainBtn.style.color = 'var(--bg)';
    mainBtn.onclick = () => chrome.tabs.create({ url: chrome.runtime.getURL('review.html') });
    skipBtn.style.display = 'none';
  }

  document.getElementById('roundCount').textContent = currentState.roundCount || 0;
  document.getElementById('studyMinutes').textContent = currentState.studyMinutes || 0;
  document.getElementById('breakMinutes').textContent = currentState.breakMinutes || 0;

  document.querySelectorAll('.ambient-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.sound === currentState.ambientSound);
  });
  updateCountdown();
}

function updateCountdown() {
  const now = new Date();
  const hour = now.getHours();
  const el = document.getElementById('countdown');
  if (hour >= DAILY_LIMIT_HOUR) {
    el.textContent = '已过 22:00，明天见！'; el.style.color = 'var(--danger)';
  } else {
    const diff = (DAILY_LIMIT_HOUR - hour - 1) * 60 + (60 - now.getMinutes());
    el.textContent = `距离 22:00 还有 ${Math.floor(diff/60)}小时${diff%60}分钟`;
    el.style.color = 'var(--muted)';
  }
}

function getRemaining() {
  if (!currentState) return 0;
  const { timerState, focusStartedAt, pausedRemaining, breakStartedAt } = currentState;
  if (timerState === 'running' && focusStartedAt) return Math.max(FOCUS_SECONDS - Math.floor((Date.now() - focusStartedAt) / 1000), 0);
  if (timerState === 'paused' && pausedRemaining) return pausedRemaining;
  if (timerState === 'resting' && breakStartedAt) return Math.max(REST_SECONDS - Math.floor((Date.now() - breakStartedAt) / 1000), 0);
  return 0;
}

function formatTime(s) { return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`; }

function startTick() {
  tickInterval = setInterval(() => {
    if (currentState?.timerState !== 'idle') {
      document.getElementById('timerDisplay').textContent = formatTime(getRemaining());
    }
    updateCountdown();
  }, 1000);
}

// ── 轮次目标弹窗 ──
function promptGoal() {
  return new Promise(resolve => {
    // 创建弹窗 DOM
    const overlay = document.createElement('div');
    overlay.className = 'goal-overlay';
    overlay.innerHTML = `
      <div class="goal-card">
        <div class="goal-title">🎯 本轮目标</div>
        <div class="goal-subtitle">这轮打算学什么？（可跳过）</div>
        <input type="text" class="goal-input" id="goalInput" placeholder="例：数学导数、英语阅读..." autofocus>
        <button class="btn btn-primary goal-submit" id="goalSubmit">开始学习</button>
      </div>`;
    document.body.appendChild(overlay);

    const input = document.getElementById('goalInput');
    const submit = document.getElementById('goalSubmit');

    const finish = () => {
      const goal = input.value.trim();
      overlay.remove();
      resolve(goal);
    };

    submit.addEventListener('click', finish);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') finish(); });
    input.focus();
  });
}

// ── 操作 ──
async function onMainBtnClick() {
  if (!currentState) return;
  const { timerState } = currentState;

  if (timerState === 'idle' || timerState === 'paused') {
    // 弹出轮次目标
    const goal = await promptGoal();
    const action = timerState === 'idle' ? 'start' : 'resume';
    chrome.runtime.sendMessage({ action, goal }, (res) => {
      if (res?.error) { alert(res.error); return; }
      currentState.timerState = 'running';
      if (action === 'start') currentState.focusStartedAt = Date.now();
      currentState.pausedRemaining = null;
      currentState.currentGoal = goal;
      render();
    });
  } else if (timerState === 'running') {
    chrome.runtime.sendMessage({ action: 'pause' }, () => {
      currentState.pausedRemaining = Math.max(FOCUS_SECONDS - Math.floor((Date.now() - currentState.focusStartedAt) / 1000), 0);
      currentState.timerState = 'paused';
      render();
    });
  }
}

function onSkip() {
  chrome.runtime.sendMessage({ action: 'skipToRest' }, () => {
    currentState.timerState = 'resting';
    currentState.breakStartedAt = Date.now();
    currentState.roundCount = (currentState.roundCount || 0) + 1;
    render();
  });
}
