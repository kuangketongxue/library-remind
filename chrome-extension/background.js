// ═══ 精力管理 — Service Worker ═══
// 状态机: idle → running → resting → idle (60+5分钟循环)
//         任何状态 → paused → running (暂停/继续)

const ALARM_PREFIX = 'rest_reminder_';
const FOCUS_MINUTES = 60;
const REST_MINUTES = 5;
const EYE_REST_INTERVAL_MINUTES = 20;
const EYE_REST_DURATION_SECONDS = 20;

// ── 状态管理 ──
let state = {
  timerState: 'idle',      // idle | running | paused | resting
  focusStartedAt: null,     // 本轮开始时间戳
  pausedRemaining: null,    // 暂停时剩余秒数
  roundCount: 0,            // 今日轮次
  studyMinutes: 0,          // 今日学习分钟
  breakMinutes: 0,          // 今日休息分钟
  lastEyeRest: null,        // 上次护眼提醒时间戳
  currentDate: null,        // 用于日期切换重置
};

// ── 初始化 ──
chrome.runtime.onInstalled.addListener(async () => {
  const saved = await chrome.storage.local.get('state');
  if (saved.state) {
    state = { ...state, ...saved.state };
  }
  updateBadge();
});

chrome.runtime.onStartup.addListener(async () => {
  const saved = await chrome.storage.local.get('state');
  if (saved.state) {
    state = { ...state, ...saved.state };
  }
  checkDateReset();
  updateBadge();
});

// ── 闹钟处理 ──
chrome.alarms.onAlarm.addListener(async (alarm) => {
  checkDateReset();

  if (alarm.name === `${ALARM_PREFIX}focus_complete`) {
    // 60分钟学习完成 → 进入休息
    state.timerState = 'resting';
    state.breakStartedAt = Date.now();
    state.roundCount++;
    state.studyMinutes += FOCUS_MINUTES;
    await saveState();
    updateBadge();

    // 通知用户
    chrome.notifications.create(`${ALARM_PREFIX}rest`, {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '⚡ 学习时间到！',
      message: `已完成第 ${state.roundCount} 轮（${FOCUS_MINUTES}分钟），休息 ${REST_MINUTES} 分钟吧！`,
      priority: 2,
      requireInteraction: true,
    });

    // 设置休息结束闹钟
    chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, {
      delayInMinutes: REST_MINUTES,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}rest_complete`) {
    // 5分钟休息完成 → 回到 idle
    state.timerState = 'idle';
    state.breakMinutes += REST_MINUTES;
    state.focusStartedAt = null;
    state.pausedRemaining = null;
    await saveState();
    updateBadge();

    chrome.notifications.create(`${ALARM_PREFIX}idle`, {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '⚡ 休息结束',
      message: `今日已学习 ${state.studyMinutes} 分钟（${state.roundCount} 轮），准备好了就继续！`,
      priority: 1,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}eye_rest`) {
    // 20-20-20 护眼提醒
    state.lastEyeRest = Date.now();
    await saveState();

    chrome.notifications.create(`${ALARM_PREFIX}eye_rest`, {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '👁️ 20-20-20 护眼',
      message: '看看 6 米以外的东西，持续 20 秒',
      priority: 2,
      requireInteraction: true,
    });
  }
});

// ── 通知点击处理 ──
chrome.notifications.onClicked.addListener(async (notifId) => {
  chrome.notifications.clear(notifId);
  // 打开 popup
  // 注意：Chrome 扩展无法程序化打开 popup，但用户可以点击图标
});

// ── 消息处理（来自 popup/options） ──
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  switch (msg.action) {
    case 'getState':
      checkDateReset();
      sendResponse({ ...state });
      break;

    case 'start':
      startFocus();
      sendResponse({ ok: true });
      break;

    case 'pause':
      pauseFocus();
      sendResponse({ ok: true });
      break;

    case 'resume':
      resumeFocus();
      sendResponse({ ok: true });
      break;

    case 'reset':
      resetAll();
      sendResponse({ ok: true });
      break;

    case 'skipToRest':
      // 跳过剩余时间，直接进入休息
      chrome.alarms.clearAll();
      state.timerState = 'resting';
      state.breakStartedAt = Date.now();
      state.roundCount++;
      state.studyMinutes += Math.floor((Date.now() - state.focusStartedAt) / 60000);
      saveState().then(() => updateBadge());
      chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, { delayInMinutes: REST_MINUTES });
      sendResponse({ ok: true });
      break;

    default:
      sendResponse({ error: 'unknown action' });
  }
  return true; // 保持消息通道
});

// ── 核心操作 ──
function startFocus() {
  chrome.alarms.clearAll();
  state.timerState = 'running';
  state.focusStartedAt = Date.now();
  state.lastEyeRest = Date.now();
  saveState().then(() => updateBadge());

  // 60分钟学习闹钟
  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, {
    delayInMinutes: FOCUS_MINUTES,
  });

  // 20-20-20 护眼闹钟
  chrome.alarms.create(`${ALARM_PREFIX}eye_rest`, {
    delayInMinutes: EYE_REST_INTERVAL_MINUTES,
    periodInMinutes: EYE_REST_INTERVAL_MINUTES,
  });
}

function pauseFocus() {
  if (state.timerState !== 'running') return;
  chrome.alarms.clearAll();
  const elapsed = Math.floor((Date.now() - state.focusStartedAt) / 1000);
  state.pausedRemaining = Math.max(FOCUS_MINUTES * 60 - elapsed, 0);
  state.timerState = 'paused';
  saveState().then(() => updateBadge());
}

function resumeFocus() {
  if (state.timerState !== 'paused' || !state.pausedRemaining) return;
  state.timerState = 'running';
  // 从暂停位置继续
  state.focusStartedAt = Date.now() - (FOCUS_MINUTES * 60 - state.pausedRemaining) * 1000;
  state.pausedRemaining = null;
  saveState().then(() => updateBadge());

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, {
    delayInMinutes: state.pausedRemaining ? state.pausedRemaining / 60 : FOCUS_MINUTES,
  });
}

function resetAll() {
  chrome.alarms.clearAll();
  state.timerState = 'idle';
  state.focusStartedAt = null;
  state.pausedRemaining = null;
  state.lastEyeRest = null;
  saveState().then(() => updateBadge());
}

// ── 辅助函数 ──
function checkDateReset() {
  const today = new Date().toISOString().slice(0, 10);
  if (state.currentDate !== today) {
    state.currentDate = today;
    state.roundCount = 0;
    state.studyMinutes = 0;
    state.breakMinutes = 0;
    state.lastEyeRest = null;
    saveState();
  }
}

function updateBadge() {
  const badges = {
    idle: { text: '', color: '#888888' },
    running: { text: '▶', color: '#78B450' },
    paused: { text: '⏸', color: '#d4a853' },
    resting: { text: '☕', color: '#d97757' },
  };
  const b = badges[state.timerState] || badges.idle;
  chrome.action.setBadgeText({ text: b.text });
  chrome.action.setBadgeBackgroundColor({ color: b.color });

  // 在 running 状态下，显示剩余分钟数
  if (state.timerState === 'running' && state.focusStartedAt) {
    const elapsed = Math.floor((Date.now() - state.focusStartedAt) / 60000);
    const remaining = Math.max(FOCUS_MINUTES - elapsed, 0);
    chrome.action.setBadgeText({ text: String(remaining) });
  }
  if (state.timerState === 'paused' && state.pausedRemaining) {
    chrome.action.setBadgeText({ text: String(Math.ceil(state.pausedRemaining / 60)) });
  }
}

async function saveState() {
  await chrome.storage.local.set({ state });
}

// 定期更新 badge（running 状态下每分钟更新剩余时间）
setInterval(() => {
  if (state.timerState === 'running') {
    updateBadge();
  }
}, 60000);
