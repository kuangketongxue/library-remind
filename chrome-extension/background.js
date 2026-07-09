// ═══ 精力管理 — Service Worker ═══
// 状态机: idle → running → resting → review → idle
//         任何状态 → paused → running

const ALARM_PREFIX = 'rest_reminder_';
const FOCUS_MINUTES = 60;
const REST_MINUTES = 5;
const EYE_REST_INTERVAL_MINUTES = 20;
const EYE_REST_EVERY_N_ROUNDS = 3;
const DAILY_LIMIT_HOUR = 22;

const BILIBILI_FAV_URL = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0';
const BILIBILI_EYE_URL = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click';

// ── 成就定义 ──
const ACHIEVEMENTS = [
  { id: 'first_hour', name: '初出茅庐', desc: '累计学习 1 小时', icon: '📖', cat: 'study', key: 'totalStudy', target: 60 },
  { id: 'ten_hours', name: '学海无涯', desc: '累计学习 10 小时', icon: '📚', cat: 'study', key: 'totalStudy', target: 600 },
  { id: 'fifty_hours', name: '废寝忘食', desc: '累计学习 50 小时', icon: '🔥', cat: 'study', key: 'totalStudy', target: 3000 },
  { id: 'hundred_hours', name: '博学多才', desc: '累计学习 100 小时', icon: '🎓', cat: 'study', key: 'totalStudy', target: 6000 },
  { id: 'streak_3', name: '三天打鱼', desc: '连续打卡 3 天', icon: '🌱', cat: 'streak', key: 'streak', target: 3 },
  { id: 'streak_7', name: '一周坚持', desc: '连续打卡 7 天', icon: '🌿', cat: 'streak', key: 'streak', target: 7 },
  { id: 'streak_14', name: '两周达人', desc: '连续打卡 14 天', icon: '🌳', cat: 'streak', key: 'streak', target: 14 },
  { id: 'streak_30', name: '月度之星', desc: '连续打卡 30 天', icon: '⭐', cat: 'streak', key: 'streak', target: 30 },
  { id: 'daily_4h', name: '半日充实', desc: '单日学习 4 小时', icon: '💪', cat: 'daily', key: 'todayStudy', target: 240 },
  { id: 'daily_8h', name: '全天奋战', desc: '单日学习 8 小时', icon: '🏆', cat: 'daily', key: 'todayStudy', target: 480 },
  { id: 'review_10', name: '反思达人', desc: '累计 10 次复盘', icon: '📝', cat: 'review', key: 'totalReviews', target: 10 },
  { id: 'review_50', name: '深度思考', desc: '累计 50 次复盘', icon: '🧠', cat: 'review', key: 'totalReviews', target: 50 },
  { id: 'perfect', name: '完美一轮', desc: '评分达到 100', icon: '💯', cat: 'review', key: 'maxScore', target: 100 },
  { id: 'rounds_10', name: '初露锋芒', desc: '累计 10 轮', icon: '🎯', cat: 'rounds', key: 'totalRounds', target: 10 },
  { id: 'rounds_50', name: '持之以恒', desc: '累计 50 轮', icon: '🏅', cat: 'rounds', key: 'totalRounds', target: 50 },
  { id: 'rounds_100', name: '百日修炼', desc: '累计 100 轮', icon: '👑', cat: 'rounds', key: 'totalRounds', target: 100 },
];

// ── 状态管理 ──
let state = {
  timerState: 'idle',
  focusStartedAt: null,
  breakStartedAt: null,
  pausedRemaining: null,
  roundCount: 0,
  studyMinutes: 0,
  breakMinutes: 0,
  lastEyeRest: null,
  currentDate: null,
  ambientSound: '',  // 当前白噪音类型
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

// ── 快捷键处理 ──
chrome.commands.onCommand.addListener((cmd) => {
  if (cmd === 'toggle-pause') {
    if (state.timerState === 'running') pauseFocus();
    else if (state.timerState === 'paused') resumeFocus();
  }
});

// ── 闹钟处理 ──
chrome.alarms.onAlarm.addListener(async (alarm) => {
  checkDateReset();

  if (alarm.name === `${ALARM_PREFIX}focus_complete`) {
    state.timerState = 'resting';
    state.breakStartedAt = Date.now();
    state.roundCount++;
    state.studyMinutes += FOCUS_MINUTES;
    await saveState();
    updateBadge();

    chrome.notifications.create(`${ALARM_PREFIX}rest`, {
      type: 'basic', iconUrl: 'icons/icon128.png',
      title: '⚡ 学习时间到！',
      message: `已完成第 ${state.roundCount} 轮（${FOCUS_MINUTES}分钟），休息 ${REST_MINUTES} 分钟吧！`,
      priority: 2, requireInteraction: true,
    });

    chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, { delayInMinutes: REST_MINUTES });
  }

  if (alarm.name === `${ALARM_PREFIX}rest_complete`) {
    state.timerState = 'review';
    state.breakMinutes += REST_MINUTES;
    state.focusStartedAt = null;
    state.pausedRemaining = null;
    await saveState();
    updateBadge();

    chrome.tabs.create({ url: 'review.html' });
    chrome.notifications.create(`${ALARM_PREFIX}review`, {
      type: 'basic', iconUrl: 'icons/icon128.png',
      title: '📝 复盘时间',
      message: `第 ${state.roundCount} 轮学习完成，请为本轮评分`,
      priority: 2, requireInteraction: true,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}eye_rest`) {
    state.lastEyeRest = Date.now();
    await saveState();

    // 打开护眼浮窗
    chrome.windows.create({
      url: 'eye-rest.html',
      type: 'popup',
      width: 400, height: 350,
      focused: true,
    });
  }

  if (alarm.name === `${ALARM_PREFIX}badge_update`) {
    updateBadge();
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
      saveReview(msg.score, msg.subject, msg.label).then(async () => {
        checkAchievements();
        if (state.roundCount % EYE_REST_EVERY_N_ROUNDS === 0) {
          chrome.tabs.create({ url: BILIBILI_EYE_URL });
        } else {
          chrome.tabs.create({ url: BILIBILI_FAV_URL });
        }
        state.timerState = 'idle';
        await saveState();
        updateBadge();
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

    case 'getAchievementStats':
      getAchievementStats().then(stats => sendResponse({ stats }));
      break;

    case 'openPage':
      chrome.tabs.create({ url: msg.url });
      sendResponse({ ok: true });
      break;

    case 'playAmbient':
      state.ambientSound = msg.sound;
      saveState();
      sendResponse({ ok: true });
      break;

    case 'stopAmbient':
      state.ambientSound = '';
      saveState();
      sendResponse({ ok: true });
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

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, { delayInMinutes: FOCUS_MINUTES });
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
  const remainingMin = state.pausedRemaining / 60;
  state.focusStartedAt = Date.now() - (FOCUS_MINUTES * 60 - state.pausedRemaining) * 1000;
  state.pausedRemaining = null;
  saveState().then(() => updateBadge());

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, { delayInMinutes: remainingMin });
  chrome.alarms.create(`${ALARM_PREFIX}eye_rest`, {
    delayInMinutes: EYE_REST_INTERVAL_MINUTES,
    periodInMinutes: EYE_REST_INTERVAL_MINUTES,
  });
}

function resetAll() {
  chrome.alarms.clearAll();
  state.timerState = 'idle';
  state.focusStartedAt = null;
  state.pausedRemaining = null;
  state.lastEyeRest = null;
  state.ambientSound = '';
  saveState().then(() => updateBadge());
}

// ── 复盘存储 ──
async function saveReview(score, subject, label) {
  const today = new Date().toISOString().slice(0, 10);
  const key = `reviews_${today}`;
  const res = await chrome.storage.local.get(key);
  const reviews = res[key] || [];
  reviews.push({
    round: state.roundCount,
    score: Math.max(1, Math.min(100, score)),
    subject: subject || '其他',
    label: label || '其他',
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
  const stats = { days: [], totalStudy: 0, totalRounds: 0, avgScore: 0 };
  let totalScore = 0, scoreCount = 0;

  for (let i = 6; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const label = `${d.getMonth() + 1}/${d.getDate()}`;
    const key = `reviews_${dateStr}`;
    const res = await chrome.storage.local.get(key);
    const reviews = res[key] || [];
    const dayScore = reviews.length > 0
      ? reviews.reduce((s, r) => s + r.score, 0) / reviews.length : 0;
    stats.days.push({ date: dateStr, label, rounds: reviews.length, avgScore: Math.round(dayScore) });
    stats.totalRounds += reviews.length;
    reviews.forEach(r => { totalScore += r.score; scoreCount++; });
  }
  stats.avgScore = scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;
  return stats;
}

// ── 成就系统 ──
async function getAchievementStats() {
  const today = new Date().toISOString().slice(0, 10);

  // 累计数据
  let totalStudy = 0, totalReviews = 0, totalRounds = 0, maxScore = 0;
  const allKeys = (await chrome.storage.local.get(null));
  for (const [k, v] of Object.entries(allKeys)) {
    if (k.startsWith('reviews_') && Array.isArray(v)) {
      v.forEach(r => {
        totalReviews++;
        if (r.score > maxScore) maxScore = r.score;
      });
    }
  }
  totalStudy = state.studyMinutes; // 简化：只计今日
  totalRounds = state.roundCount;

  // 连续打卡
  let streak = 0;
  const d = new Date();
  for (let i = 0; i < 365; i++) {
    const ds = d.toISOString().slice(0, 10);
    const key = `reviews_${ds}`;
    const res = await chrome.storage.local.get(key);
    if (res[key] && res[key].length > 0) {
      streak++;
      d.setDate(d.getDate() - 1);
    } else break;
  }

  return {
    totalStudy, totalReviews, totalRounds, maxScore,
    streak, todayStudy: state.studyMinutes,
  };
}

async function checkAchievements() {
  const stats = await getAchievementStats();
  const res = await chrome.storage.local.get('unlocked_achievements');
  const unlocked = new Set(res.unlocked_achievements || []);

  ACHIEVEMENTS.forEach(a => {
    if (unlocked.has(a.id)) return;
    const val = stats[a.key] || 0;
    if (val >= a.target) {
      unlocked.add(a.id);
      chrome.notifications.create(`ach_${a.id}`, {
        type: 'basic', iconUrl: 'icons/icon128.png',
        title: `${a.icon} 成就解锁！`,
        message: `${a.name} — ${a.desc}`,
        priority: 1,
      });
    }
  });

  await chrome.storage.local.set({ unlocked_achievements: [...unlocked] });
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

// badge 每分钟更新
setInterval(() => {
  if (state.timerState !== 'idle') updateBadge();
}, 60000);
