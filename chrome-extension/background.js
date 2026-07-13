// ═══ 精力管理 — Service Worker ═══
// 状态机: idle → running → resting → review → idle
//         任何状态 → paused → running

const ALARM_PREFIX = 'rest_reminder_';
const FOCUS_MINUTES_DEFAULT = 60;
const REST_MINUTES_DEFAULT = 5;
const EYE_REST_INTERVAL_DEFAULT = 20;
const EYE_REST_EVERY_N_ROUNDS = 3;
const DAILY_LIMIT_HOUR = 22;

const BILIBILI_FAV_DEFAULT = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0';
const BILIBILI_EYE_DEFAULT = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click';

// ── 读取用户设置（每次都读最新，不缓存）──
async function getSettings() {
  const res = await chrome.storage.local.get('settings');
  const s = res.settings || {};
  return {
    focusMinutes: Math.max(15, parseInt(s.focusMinutes) || FOCUS_MINUTES_DEFAULT),
    restMinutes: Math.max(1, parseInt(s.restMinutes) || REST_MINUTES_DEFAULT),
    eyeRestInterval: Math.max(5, parseInt(s.eyeRestInterval) || EYE_REST_INTERVAL_DEFAULT),
    autoStartNext: s.autoStartNext === true,
    soundEnabled: s.soundEnabled !== false, // 默认开
  };
}

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
  ambientSound: '',
  grayscale: false,
  pausedCount: 0,
  focusMinutes: FOCUS_MINUTES_DEFAULT,
  restMinutes: REST_MINUTES_DEFAULT,
  eyeRestInterval: EYE_REST_INTERVAL_DEFAULT,
};

// ── 灰阶滤镜 CSS ──
const GRAYSCALE_CSS = 'html, body { filter: grayscale(100%) !important; }';

// ── 灰阶滤镜注入 ──
async function enableGrayscale() {
  try {
    if (!chrome.scripting || !chrome.tabs) return false;
    const tabs = await chrome.tabs.query({});
    const results = await Promise.allSettled(
      tabs
        .filter(t => t.url && !t.url.startsWith('chrome://') && !t.url.startsWith('chrome-extension://') && !t.url.startsWith('about:'))
        .map(t => chrome.scripting.insertCSS({
          target: { tabId: t.id },
          css: GRAYSCALE_CSS,
        }))
    );
    return results.filter(r => r.status === 'fulfilled').length > 0;
  } catch (e) { console.error('Grayscale enable failed:', e); return false; }
}

async function disableGrayscale() {
  try {
    if (!chrome.scripting || !chrome.tabs) return false;
    const tabs = await chrome.tabs.query({});
    await Promise.allSettled(
      tabs
        .filter(t => t.url && !t.url.startsWith('chrome://') && !t.url.startsWith('chrome-extension://') && !t.url.startsWith('about:'))
        .map(t => chrome.scripting.removeCSS({
          target: { tabId: t.id },
          css: GRAYSCALE_CSS,
        }))
    );
    return true;
  } catch (e) { console.error('Grayscale disable failed:', e); return false; }
}

// ── 动态图标生成 (OffscreenCanvas) ──
function generateIcon(state) {
  const SIZE = 128;
  let remaining = 0;
  let progress = 0;
  const now = Date.now();

  if (state.timerState === 'running' && state.focusStartedAt) {
    const elapsed = (now - state.focusStartedAt) / 60000;
    remaining = Math.max(0, Math.ceil(state.focusMinutes - elapsed));
    progress = Math.min(elapsed / state.focusMinutes, 1);
  } else if (state.timerState === 'paused' && state.pausedRemaining) {
    remaining = Math.max(0, Math.ceil(state.pausedRemaining / 60));
    progress = 0;
  } else if (state.timerState === 'resting' && state.breakStartedAt) {
    const elapsed = (now - state.breakStartedAt) / 60000;
    remaining = Math.max(0, Math.ceil(state.restMinutes - elapsed));
    progress = Math.min(elapsed / state.restMinutes, 1);
  }

  const canvas = new OffscreenCanvas(SIZE, SIZE);
  const ctx = canvas.getContext('2d');
  const cx = SIZE / 2, cy = SIZE / 2, r = SIZE / 2 - 4;

  // 背景
  const bgColors = { idle: '#1a1a24', running: '#0a2a0a', paused: '#2a2a0a', resting: '#2a1a0a', review: '#2a240a' };
  ctx.fillStyle = bgColors[state.timerState] || '#1a1a24';
  ctx.fillRect(0, 0, SIZE, SIZE);

  // 进度环 (底色)
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 6;
  ctx.stroke();

  // 进度环 (前景)
  if (progress > 0) {
    const accentColors = { running: '#78B450', resting: '#d97757', review: '#d4af37', paused: '#d4a853' };
    ctx.beginPath();
    ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * progress);
    ctx.strokeStyle = accentColors[state.timerState] || '#d4af37';
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.stroke();
  }

  // 数字
  let text = '';
  if (state.timerState === 'running') text = String(remaining);
  else if (state.timerState === 'paused') text = '⏸';
  else if (state.timerState === 'resting') text = '☕';
  else if (state.timerState === 'review') text = '📝';
  else text = '⚡';

  const fontSize = text.length >= 3 ? 36 : text.length >= 2 ? 44 : 56;
  ctx.font = `700 ${fontSize}px 'Segoe UI', sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(text, cx, cy + 2);

  return canvas.convertToBlob('image/png');
}

async function updateIcon() {
  try {
    const blob = await generateIcon(state);
    const bitmap = await createImageBitmap(blob);
    const ctx = new OffscreenCanvas(bitmap.width, bitmap.height).getContext('2d');
    ctx.drawImage(bitmap, 0, 0);
    const imageData = ctx.getImageData(0, 0, bitmap.width, bitmap.height);
    await chrome.action.setIcon({ imageData: { 128: imageData } });
  } catch (e) { console.error('Icon update failed:', e); }
}

// ── 深度专注评分算法 ──
// 公式: 深度分 = 自评分 × 完成度系数 × 专注度系数 × 连续性系数
//   - 完成度系数: 本轮实际学习时长 / 计划时长 (0.6 ~ 1.0)
//   - 专注度系数: 1 - (暂停次数 × 0.08) (最低 0.6)
//   - 连续性系数: 基于连续打卡天数 (0.8 ~ 1.0)
function computeDeepScore(selfScore, roundStudyMinutes, pausedCount, streak = 0) {
  const completion = Math.min(Math.max(roundStudyMinutes / state.focusMinutes, 0.6), 1.0);
  const focus = Math.max(1 - (pausedCount || 0) * 0.08, 0.6);
  const continuity = Math.min(0.8 + (streak || 0) * 0.01, 1.0);
  const raw = selfScore * completion * focus * continuity;
  return {
    score: Math.round(raw),
    completion: Math.round(completion * 100),
    focus: Math.round(focus * 100),
    continuity: Math.round(continuity * 100),
  };
}

// ── 初始化 ──
async function syncSettingsToState() {
  const s = await getSettings();
  state.focusMinutes = s.focusMinutes;
  state.restMinutes = s.restMinutes;
  state.eyeRestInterval = s.eyeRestInterval;
}

chrome.runtime.onInstalled.addListener(async () => {
  const saved = await chrome.storage.local.get('state');
  if (saved.state) state = { ...state, ...saved.state };
  await syncSettingsToState();
  updateBadge();
  chrome.alarms.create(`${ALARM_PREFIX}badge_update`, { periodInMinutes: 1 });
});

chrome.runtime.onStartup.addListener(async () => {
  const saved = await chrome.storage.local.get('state');
  if (saved.state) state = { ...state, ...saved.state };
  await syncSettingsToState();
  checkDateReset();
  updateBadge();
});

// ── 闹钟处理 ──
chrome.alarms.onAlarm.addListener(async (alarm) => {
  checkDateReset();
  const s = await getSettings();

  if (alarm.name === `${ALARM_PREFIX}focus_complete`) {
    state.timerState = 'resting';
    state.breakStartedAt = Date.now();
    state.roundCount++;
    state.studyMinutes += s.focusMinutes;
    await saveState();
    updateBadge();

    chrome.windows.create({
      url: 'rest.html',
      type: 'popup',
      width: 400, height: 420,
      focused: true,
    });

    chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, { delayInMinutes: s.restMinutes });
  }

  if (alarm.name === `${ALARM_PREFIX}rest_complete`) {
    if (state.timerState !== 'resting') return;
    state.timerState = 'review';
    state.breakMinutes += s.restMinutes;
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

  if (alarm.name === `${ALARM_PREFIX}pause_remind`) {
    if (state.timerState !== 'paused') return;
    chrome.notifications.create(`${ALARM_PREFIX}pause_remind`, {
      type: 'basic', iconUrl: 'icons/icon128.png',
      title: '⏸ 已暂停 2 分钟',
      message: '继续学习？还是结束本轮去休息？',
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
      getStreak().then(async streak => {
        const s = await getSettings();
        sendResponse({
          ...state,
          streak,
          hour: new Date().getHours(),
          minute: new Date().getMinutes(),
          focusMinutes: s.focusMinutes,
          restMinutes: s.restMinutes,
          eyeRestInterval: s.eyeRestInterval,
          autoStartNext: s.autoStartNext,
          soundEnabled: s.soundEnabled,
        });
      });
      break;

    case 'start':
      if (new Date().getHours() >= DAILY_LIMIT_HOUR) {
        sendResponse({ error: `已过 ${DAILY_LIMIT_HOUR}:00，明天再开始吧` });
        break;
      }
      startFocus(msg.goal);
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
      chrome.alarms.create(`${ALARM_PREFIX}rest_complete`, { delayInMinutes: state.restMinutes });
      sendResponse({ ok: true });
      break;

    case 'submitReview': {
      saveReview(msg.score, msg.subject, msg.label, msg.deepScore).then(async () => {
        checkAchievements();
        const s = await getSettings();
        const settings = s;
        if (state.roundCount % EYE_REST_EVERY_N_ROUNDS === 0) {
          chrome.tabs.create({ url: settings.bilibiliEyeUrl || BILIBILI_EYE_DEFAULT });
        } else {
          chrome.tabs.create({ url: settings.bilibiliFavUrl || BILIBILI_FAV_DEFAULT });
        }
        state.timerState = 'idle';
        await saveState();
        updateBadge();
        // 自动开始下一轮（延时 3 秒让用户看到"已提交"反馈）
        if (settings.autoStartNext) {
          setTimeout(() => startFocus(), 3000);
        }
        sendResponse({ ok: true });
      });
      break;
    }

    case 'toggleGrayscale': {
      state.grayscale = !state.grayscale;
      await saveState();
      if (state.grayscale && state.timerState === 'running') {
        await enableGrayscale();
      } else {
        await disableGrayscale();
      }
      updateBadge();
      sendResponse({ ok: true, grayscale: state.grayscale });
      break;
    }

    case 'getGrayscale':
      sendResponse({ grayscale: state.grayscale });
      break;

    case 'submitRest': {
      // rest.html 倒计时结束，进入复盘
      if (state.timerState !== 'resting') break;
      state.timerState = 'review';
      state.breakMinutes += state.restMinutes;
      state.focusStartedAt = null;
      state.pausedRemaining = null;
      chrome.alarms.clear(`${ALARM_PREFIX}rest_complete`); // 清除备份报警
      saveState().then(() => updateBadge());
      chrome.tabs.create({ url: 'review.html' });
      sendResponse({ ok: true });
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

    case 'getStreak':
      getStreak().then(streak => sendResponse({ streak }));
      break;

    case 'exportData':
      exportData().then(json => sendResponse({ json }));
      break;

    default:
      sendResponse({ error: 'unknown action' });
  }
  return true;
});

// ── 核心操作 ──
async function startFocus(goal) {
  const s = await getSettings();
  chrome.alarms.clearAll();
  state.timerState = 'running';
  state.focusStartedAt = Date.now();
  state.lastEyeRest = Date.now();
  state.pausedCount = 0;
  if (goal) state.currentGoal = goal;
  await saveState();
  updateBadge();

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, { delayInMinutes: s.focusMinutes });
  chrome.alarms.create(`${ALARM_PREFIX}eye_rest`, {
    delayInMinutes: s.eyeRestInterval,
    periodInMinutes: s.eyeRestInterval,
  });
  if (state.grayscale) enableGrayscale();
}

async function pauseFocus() {
  if (state.timerState !== 'running') return;
  const s = await getSettings();
  chrome.alarms.clearAll();
  const elapsed = Math.floor((Date.now() - state.focusStartedAt) / 1000);
  state.pausedRemaining = Math.max(s.focusMinutes * 60 - elapsed, 0);
  state.timerState = 'paused';
  state.pausedCount = (state.pausedCount || 0) + 1;
  await saveState();
  updateBadge();
  // 暂停 2 分钟后提醒
  chrome.alarms.create(`${ALARM_PREFIX}pause_remind`, { delayInMinutes: 2 });
}

async function resumeFocus() {
  if (state.timerState !== 'paused' || !state.pausedRemaining) return;
  const s = await getSettings();
  state.timerState = 'running';
  const remainingMin = state.pausedRemaining / 60;
  state.focusStartedAt = Date.now() - (s.focusMinutes * 60 - state.pausedRemaining) * 1000;
  state.pausedRemaining = null;
  chrome.alarms.clear(`${ALARM_PREFIX}pause_remind`);
  await saveState();
  updateBadge();

  chrome.alarms.create(`${ALARM_PREFIX}focus_complete`, { delayInMinutes: remainingMin });
  chrome.alarms.create(`${ALARM_PREFIX}eye_rest`, {
    delayInMinutes: s.eyeRestInterval,
    periodInMinutes: s.eyeRestInterval,
  });
}

function resetAll() {
  chrome.alarms.clearAll();
  state.timerState = 'idle';
  state.focusStartedAt = null;
  state.pausedRemaining = null;
  state.lastEyeRest = null;
  state.ambientSound = '';
  state.pausedCount = 0;
  saveState().then(() => updateBadge());
  if (state.grayscale) disableGrayscale();
}

// ── 复盘存储 ──
async function saveReview(score, subject, label, deepScore) {
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
    deepScore: deepScore || null,
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

// ── 连续打卡 ──
async function getStreak() {
  let streak = 0;
  const d = new Date();
  for (let i = 0; i < 365; i++) {
    const ds = d.toISOString().slice(0, 10);
    const key = `reviews_${ds}`;
    const res = await chrome.storage.local.get(key);
    if (res[key] && res[key].length > 0) {
      streak++;
      d.setDate(d.getDate() - 1);
    } else if (i === 0) {
      // 今天还没复盘，检查昨天
      d.setDate(d.getDate() - 1);
      continue;
    } else {
      break;
    }
  }
  return streak;
}

// ── 数据导出 ──
async function exportData() {
  const allData = await chrome.storage.local.get(null);
  const exportObj = { exportDate: new Date().toISOString(), data: {} };
  for (const [k, v] of Object.entries(allData)) {
    exportObj.data[k] = v;
  }
  return JSON.stringify(exportObj, null, 2);
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
  updateIcon();

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
    const remaining = Math.max(state.focusMinutes - elapsed, 0);
    chrome.action.setBadgeText({ text: String(remaining) });
  } else if (state.timerState === 'resting' && state.breakStartedAt) {
    const elapsed = Math.floor((Date.now() - state.breakStartedAt) / 60000);
    const remaining = Math.max(state.restMinutes - elapsed, 0);
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
