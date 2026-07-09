// ═══ 精力管理 — Popup 逻辑 ═══

const FOCUS_SECONDS = 60 * 60;
const REST_SECONDS = 5 * 60;

let currentState = null;
let tickInterval = null;

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', async () => {
  // 获取当前状态
  chrome.runtime.sendMessage({ action: 'getState' }, (res) => {
    currentState = res;
    render();
    startTick();
  });

  // 按钮事件
  document.getElementById('mainBtn').addEventListener('click', onMainBtnClick);
  document.getElementById('skipBtn').addEventListener('click', onSkip);
  document.getElementById('optionsLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
});

// ── 渲染 ──
function render() {
  if (!currentState) return;
  const { timerState } = currentState;

  // 状态标签
  const badge = document.getElementById('statusBadge');
  badge.className = `status-badge ${timerState}`;
  const stateNames = { idle: '待机', running: '学习中', paused: '已暂停', resting: '休息中' };
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
  };
  subtitle.textContent = subtitles[timerState] || '';

  // 主按钮
  const mainBtn = document.getElementById('mainBtn');
  const skipBtn = document.getElementById('skipBtn');
  if (timerState === 'idle') {
    mainBtn.textContent = '▶ 开始学习';
    mainBtn.className = 'btn btn-primary';
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
    mainBtn.style.background = '#d4af37';
    mainBtn.style.color = '#0d0d12';
    skipBtn.style.display = 'none';
  } else if (timerState === 'resting') {
    mainBtn.textContent = '⏸ 休息中...';
    mainBtn.className = 'btn btn-secondary';
    skipBtn.style.display = 'none';
  }

  // 统计
  document.getElementById('roundCount').textContent = currentState.roundCount || 0;
  document.getElementById('studyMinutes').textContent = currentState.studyMinutes || 0;
  document.getElementById('breakMinutes').textContent = currentState.breakMinutes || 0;
}

function getRemaining() {
  if (!currentState) return 0;
  const { timerState, focusStartedAt, pausedRemaining } = currentState;

  if (timerState === 'running' && focusStartedAt) {
    const elapsed = Math.floor((Date.now() - focusStartedAt) / 1000);
    return Math.max(FOCUS_SECONDS - elapsed, 0);
  }
  if (timerState === 'paused' && pausedRemaining) {
    return pausedRemaining;
  }
  if (timerState === 'resting' && currentState.breakStartedAt) {
    const elapsed = Math.floor((Date.now() - currentState.breakStartedAt) / 1000);
    return Math.max(REST_SECONDS - elapsed, 0);
  }
  return 0;
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// ── 定时刷新 ──
function startTick() {
  if (tickInterval) clearInterval(tickInterval);
  tickInterval = setInterval(() => {
    if (currentState && currentState.timerState !== 'idle') {
      const display = document.getElementById('timerDisplay');
      display.textContent = formatTime(getRemaining());
    }
  }, 1000);
}

// ── 操作 ──
function onMainBtnClick() {
  if (!currentState) return;
  const { timerState } = currentState;

  if (timerState === 'idle' || timerState === 'paused') {
    const action = timerState === 'idle' ? 'start' : 'resume';
    chrome.runtime.sendMessage({ action }, (res) => {
      currentState.timerState = 'running';
      if (action === 'start') {
        currentState.focusStartedAt = Date.now();
        currentState.roundCount = currentState.roundCount || 0;
      }
      currentState.pausedRemaining = null;
      render();
    });
  } else if (timerState === 'running') {
    chrome.runtime.sendMessage({ action: 'pause' }, (res) => {
      const elapsed = Math.floor((Date.now() - currentState.focusStartedAt) / 1000);
      currentState.pausedRemaining = Math.max(FOCUS_SECONDS - elapsed, 0);
      currentState.timerState = 'paused';
      render();
    });
  }
}

function onSkip() {
  chrome.runtime.sendMessage({ action: 'skipToRest' }, (res) => {
    currentState.timerState = 'resting';
    currentState.breakStartedAt = Date.now();
    currentState.roundCount = (currentState.roundCount || 0) + 1;
    render();
  });
}
