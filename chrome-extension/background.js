// ═══ 精力管理 — Service Worker ═══
// 状态机: idle → running → resting → review → idle (60+5分钟循环+复盘)
//         任何状态 → paused → running (暂停/继续)

const ALARM_PREFIX = 'rest_reminder_';
const FOCUS_MINUTES = 60;
const REST_MINUTES = 5;
const EYE_REST_INTERVAL_MINUTES = 20;
const EYE_REST_EVERY_N_ROUNDS = 3; // 每3轮打开护眼视频
const DAILY_LIMIT_HOUR = 22; // 22点后不再开始新轮次

const BILIBILI_FAV_URL = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0';
const BILIBILI_EYE_URL = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click';

// ── 状态管理 ──
let state = {
  timerState: 'idle',      // idle | running | paused | resting | review
  focusStartedAt: null,     // 本轮开始时间戳
  breakStartedAt: null,     // 休息开始时间戳
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
  if (saved.state) state = { ...state, ...saved.state };
  updateBadge();
});

chrome.runtime.onStartup.addListener(async () => {
  const saved = await chrome.storage.local.get('state');
  if (saved.state) state = { ...state, ...saved.state };
  checkDateReset();
  updateBadge();
});

// ── 闹钟处理 ──
chrome.alarms.onAlarm.addListener(async (alarm) => {
  checkDateReset();

  if (alarm.name === `${ALARM_PREFIX}focus_complete`) {
    // 60分钟学习完成 → 进入5分钟休息
    state.timerState = 'resting';
    state.breakStartedAt = Date.now();
    state.roundCount++;
    state.studyMinutes += FOCUS_MINUTES;
    await saveState();
    updateBadge();

    chrome.notifications.create(`${ALARM_PREFIX}rest`, {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '⚡ 学习时间到！',
      message: `已完成第 ${state.roundCount} 轮（${FOCUS_MINUTES}分钟），休息 ${REST_MINUTES} 分钟吧！`,
      priority: 2,
      requireInteraction: true,
    });

    // 5分钟后休息结束 → 弹出复盘
    chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, {
      delayInMinutes: REST_MINUTES,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}rest_complete`) {
    // 5分钟休息完成 → 弹出复盘窗口
    state.timerState = 'review';
    state.breakMinutes += REST_MINUTES;
    state.focusStartedAt = null;
    state.pausedRemaining = null;
    await saveState();
    updateBadge();

    // 打开复盘页面
    chrome.tabs.create({ url: 'review.html' });

    chrome.notifications.create(`${ALARM_PREFIX}review`, {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '📝 复盘时间',
      message: `第 ${state.roundCount} 轮学习完成，请为本轮评分（1-100）`,
      priority: 2,
      requireInteraction: true,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}eye_rest`) {
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

// ── 通知点击 ──
chrome.notifications.onClicked.addListener((notifId) => {
  chrome.notifications.clear(notifId);
});

// ── 消息处理 ──
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  switch (msg.action) {
    case 'getState':
      checkDateReset();
      sendResponse({ ...state, hour: new Date().getHours(), minute: new Date().getMinutes() });
      break;

    case 'start':
      if (new Date().getHours() >= DAILY_LIMIT_HOUR) {
        sendResponse({ error: `已过 ${DAILY_LIMIT_HOUR}:00，明天再开始吧` });
        break;
      }
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
      chrome.alarms.clearAll();
      state.timerState = 'resting';
      state.breakStartedAt = Date.now();
      state.roundCount++;
      state.studyMinutes += Math.floor((Date.now() - state.focusStartedAt) / 60000);
      saveState().then(() => updateBadge());
      chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, { delayInMinutes: REST_MINUTES });
      sendResponse({ ok: true });
      break;

    case 'submitReview': {
      // 保存复盘评分
      const { score } = msg;
      saveReview(score).then(() => {
        // 根据轮次打开不同 B 站链接
        if (state.roundCount % EYE_REST_EVERY_N_ROUNDS === 0) {
          chrome.tabs.create({ url: BILIBILI_EYE_URL });
        } else {
          chrome.tabs.create({ url: BILIBILI_FAV_URL });
        }
        // 回到 idle
        state.timerState = 'idle';
        saveState().then(() => updateBadge());
        sendResponse({ ok: true });
      });
      break;
    }

    case 'getReviews':
      getReviews(msg.date).then(reviews => sendResponse({ reviews }));
      break;

    case 'getStats':
      getStats().then(stats => sendResponse({ stats }));
      break;

    default:
      sendResponse({ error: 'unknown action' });
  }
  return true;
});

// ── 核心操作 ──
function startFocus() {
  chrome.alarms.clearAll();
  state.timerState = 'running';
  state.focusStartedAt = Date.now();
  state.lastEyeRest = Date.now();
  saveState().then(() => updateBadge());

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, {
    delayInMinutes: FOCUS_MINUTES,
  });
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
  state.focusStartedAt = Date.now() - (FOCUS_MINUTES * 60 - state.pausedRemaining) * 1000;
  const remainingMin = state.pausedRemaining / 60;
  state.pausedRemaining = null;
  saveState().then(() => updateBadge());

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, {
    delayInMinutes: remainingMin,
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

// ── 复盘存储 ──
async function saveReview(score) {
  const today = new Date().toISOString().slice(0, 10);
  const key = `reviews_${today}`;
  const res = await chrome.storage.local.get(key);
  const reviews = res[key] || [];
  reviews.push({
    round: state.roundCount,
    score: Math.max(1, Math.min(100, score)),
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    timestamp: Date.now(),
  });
  await chrome.storage.local.set({ [key]: reviews });
}

async function getReviews(date) {
  const key = `reviews_${date}`;
  const res = await chrome.storage.local.get(key);
  return res[key] || [];
}

async function getStats() {
  // 获取最近7天的统计
  const stats = { days: [], totalStudy: 0, totalRounds: 0, avgScore: 0 };
  let totalScore = 0;
  let scoreCount = 0;

  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const label = `${d.getMonth() + 1}/${d.getDate()}`;
    const key = `reviews_${dateStr}`;
    const res = await chrome.storage.local.get(key);
    const reviews = res[key] || [];
    const dayScore = reviews.length > 0
      ? reviews.reduce((s, r) => s + r.score, 0) / reviews.length
      : 0;
    stats.days.push({ date: dateStr, label, rounds: reviews.length, avgScore: Math.round(dayScore) });
    stats.totalRounds += reviews.length;
    reviews.forEach(r => { totalScore += r.score; scoreCount++; });
  }
  stats.avgScore = scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;
  return stats;
}

// ── 辅助 ──
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
    running: { text: '', color: '#78B450' },
    paused: { text: '⏸', color: '#d4a853' },
    resting: { text: '☕', color: '#d97757' },
    review: { text: '📝', color: '#d4af37' },
  };
  const b = badges[state.timerState] || badges.idle;
  chrome.action.setBadgeBackgroundColor({ color: b.color });

  if (state.timerState === 'running' && state.focusStartedAt) {
    const elapsed = Math.floor((Date.now() - state.focusStartedAt) / 60000);
    const remaining = Math.max(FOCUS_MINUTES - elapsed, 0);
    chrome.action.setBadgeText({ text: String(remaining) });
  } else if (state.timerState === 'resting' && state.breakStartedAt) {
    const elapsed = Math.floor((Date.now() - state.breakStartedAt) / 60000);
    const remaining = Math.max(REST_MINUTES - elapsed, 0);
    chrome.action.setBadgeText({ text: `${remaining}☕` });
  } else if (state.timerState === 'paused' && state.pausedRemaining) {
    chrome.action.setBadgeText({ text: String(Math.ceil(state.pausedRemaining / 60)) });
  } else {
    chrome.action.setBadgeText({ text: b.text });
  }
}

async function saveState() {
  await chrome.storage.local.set({ state });
}

// 定期更新 badge
setInterval(() => {
  if (state.timerState !== 'idle') updateBadge();
}, 60000);
