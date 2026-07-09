// ═══ 精力管理 — Popup 逻辑 ═══

const FOCUS_SECONDS = 60 * 60;
const REST_SECONDS = 5 * 60;
const DAILY_LIMIT_HOUR = 22;

let currentState = null;
let tickInterval = null;

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', async () => {
  chrome.runtime.sendMessage({ action: 'getState' }, (res) => {
    currentState = res;
    render();
    startTick();
  });

  document.getElementById('mainBtn').addEventListener('click', onMainBtnClick);
  document.getElementById('skipBtn').addEventListener('click', onSkip);
  document.getElementById('optionsLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
  document.getElementById('trendsLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: chrome.runtime.getURL('trends.html') });
  });
});

// ── 渲染 ──
function render() {
  if (!currentState) return;
  const { timerState } = currentState;

  // 状态标签
  const badge = document.getElementById('statusBadge');
  badge.className = `status-badge ${timerState}`;
  const stateNames = { idle: '待机', running: '学习中', paused: '已暂停', resting: '休息中', review: '复盘中' };
  badge.textContent = stateNames[timerState] || timerState;

  // 计时器
  const display = document.getElementById('timerDisplay');
  display.className = `timer-display ${timerState}`;
  display.textContent = formatTime(getRemaining());

  // 副标题
  const subtitle = document.getElementById('subtitle');
  const subtitles = {
    idle: '点击开始学习',
    running: '保持专注 💪',
    paused: '已暂停，点击继续',
    resting: '休息一下 ☕',
    review: '请为本轮评分',
  };
  subtitle.textContent = subtitles[timerState] || '';

  // 主按钮
  const mainBtn = document.getElementById('mainBtn');
  const skipBtn = document.getElementById('skipBtn');
  mainBtn.style.background = '';
  mainBtn.style.color = '';

  if (timerState === 'idle') {
    const hour = currentState.hour || new Date().getHours();
    if (hour >= DAILY_LIMIT_HOUR) {
      mainBtn.textContent = `⏰ ${DAILY_LIMIT_HOUR}:00 后休息`;
      mainBtn.className = 'btn btn-secondary';
      mainBtn.disabled = true;
    } else {
      mainBtn.textContent = '▶ 开始学习';
      mainBtn.className = 'btn btn-primary';
      mainBtn.disabled = false;
    }
    skipBtn.style.display = 'none';
  } else if (timerState === 'running') {
    mainBtn.textContent = '⏸ 暂停';
    mainBtn.className = 'btn btn-primary';
    mainBtn.style.background = '#d97757';
    mainBtn.style.color = '#fff';
    skipBtn.style.display = 'block';
  } else if (timerState === 'paused') {
    mainBtn.textContent = '▶ 继续';
    mainBtn.className = 'btn btn-primary';
    skipBtn.style.display = 'none';
  } else if (timerState === 'resting') {
    mainBtn.textContent = '☕ 休息中...';
    mainBtn.className = 'btn btn-secondary';
    mainBtn.disabled = true;
    skipBtn.style.display = 'none';
  } else if (timerState === 'review') {
    mainBtn.textContent = '📝 去复盘';
    mainBtn.className = 'btn btn-primary';
    mainBtn.style.background = '#d4af37';
    mainBtn.style.color = '#0d0d12';
    mainBtn.onclick = () => chrome.tabs.create({ url: chrome.runtime.getURL('review.html') });
    skipBtn.style.display = 'none';
  }

  // 统计
  document.getElementById('roundCount').textContent = currentState.roundCount || 0;
  document.getElementById('studyMinutes').textContent = currentState.studyMinutes || 0;
  document.getElementById('breakMinutes').textContent = currentState.breakMinutes || 0;

  // 22:00 倒计时
  updateCountdown();
}

function updateCountdown() {
  const now = new Date();
  const hour = now.getHours();
  const limitEl = document.getElementById('countdown');
  if (hour >= DAILY_LIMIT_HOUR) {
    limitEl.textContent = '已过 22:00，明天见！';
    limitEl.style.color = '#c95454';
  } else {
    const diff = (DAILY_LIMIT_HOUR - hour - 1) * 60 + (60 - now.getMinutes());
    const h = Math.floor(diff / 60);
    const m = diff % 60;
    limitEl.textContent = `距离 22:00 还有 ${h}小时${m}分钟`;
    limitEl.style.color = '#666';
  }
}

function getRemaining() {
  if (!currentState) return 0;
  const { timerState, focusStartedAt, pausedRemaining, breakStartedAt } = currentState;

  if (timerState === 'running' && focusStartedAt) {
    const elapsed = Math.floor((Date.now() - focusStartedAt) / 1000);
    return Math.max(FOCUS_SECONDS - elapsed, 0);
  }
  if (timerState === 'paused' && pausedRemaining) {
    return pausedRemaining;
  }
  if (timerState === 'resting' && breakStartedAt) {
    const elapsed = Math.floor((Date.now() - breakStartedAt) / 1000);
    return Math.max(REST_SECONDS - elapsed, 0);
  }
  return 0;
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function startTick() {
  if (tickInterval) clearInterval(tickInterval);
  tickInterval = setInterval(() => {
    if (currentState && currentState.timerState !== 'idle') {
      document.getElementById('timerDisplay').textContent = formatTime(getRemaining());
    }
    updateCountdown();
  }, 1000);
}

// ── 操作 ──
function onMainBtnClick() {
  if (!currentState) return;
  const { timerState } = currentState;

  if (timerState === 'idle' || timerState === 'paused') {
    const action = timerState === 'idle' ? 'start' : 'resume';
    chrome.runtime.sendMessage({ action }, (res) => {
      if (res && res.error) {
        alert(res.error);
        return;
      }
      currentState.timerState = 'running';
      if (action === 'start') {
        currentState.focusStartedAt = Date.now();
      }
      currentState.pausedRemaining = null;
      render();
    });
  } else if (timerState === 'running') {
    chrome.runtime.sendMessage({ action: 'pause' }, () => {
      const elapsed = Math.floor((Date.now() - currentState.focusStartedAt) / 1000);
      currentState.pausedRemaining = Math.max(FOCUS_SECONDS - elapsed, 0);
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
