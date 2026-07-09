// ═══ 精力管理 — Options 逻辑 ═══

const WORKER_BASE = 'https://crazy-rest-reminder.pages.dev';

document.addEventListener('DOMContentLoaded', () => {
  // 加载设置
  chrome.storage.local.get(['settings'], (res) => {
    const s = res.settings || {};
    document.getElementById('focusMinutes').value = s.focusMinutes || 60;
    document.getElementById('restMinutes').value = s.restMinutes || 5;
    document.getElementById('eyeRestInterval').value = s.eyeRestInterval || 20;
    document.getElementById('notificationsEnabled').checked = s.notificationsEnabled !== false;
    document.getElementById('feishuEnabled').checked = s.feishuEnabled || false;
    document.getElementById('mailEnabled').checked = s.mailEnabled || false;
    document.getElementById('mailTo').value = s.mailTo || '';
    document.getElementById('ghToken').value = s.ghToken || '';
    document.getElementById('ghRepo').value = s.ghRepo || '';
  });

  // 自动保存
  document.querySelectorAll('input').forEach(input => {
    input.addEventListener('change', saveSettings);
  });

  // 测试邮件
  document.getElementById('testMailBtn').addEventListener('click', async () => {
    const to = document.getElementById('mailTo').value.trim();
    if (!to) { showStatus('mailStatus', '请填写收件人', false); return; }
    saveSettings();
    showStatus('mailStatus', '发送中...', null);
    try {
      const resp = await fetch(`${WORKER_BASE}/api/send-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to,
          subject: '⚡ 精力管理 — 测试邮件',
          html: '<h2>测试成功！</h2><p>你的精力管理周报将发送到这个邮箱。</p>',
        }),
      });
      const data = await resp.json();
      showStatus('mailStatus', data.ok ? '✓ 发送成功' : `✗ ${data.error}`, data.ok);
    } catch (e) {
      showStatus('mailStatus', `✗ ${e.message}`, false);
    }
  });

  // GitHub 验证
  document.getElementById('ghVerifyBtn').addEventListener('click', async () => {
    const token = document.getElementById('ghToken').value.trim();
    const repo = document.getElementById('ghRepo').value.trim();
    if (!token || !repo) { showStatus('ghStatus', '请填写 Token 和仓库名', false); return; }
    showStatus('ghStatus', '验证中...', null);
    try {
      const resp = await fetch(`https://api.github.com/repos/${repo}`, {
        headers: { 'Authorization': `token ${token}`, 'User-Agent': 'RestReminder-Extension' },
      });
      if (resp.ok) {
        showStatus('ghStatus', '✓ 连接成功', true);
      } else {
        showStatus('ghStatus', `✗ HTTP ${resp.status}`, false);
      }
    } catch (e) {
      showStatus('ghStatus', `✗ ${e.message}`, false);
    }
  });

  // GitHub 备份
  document.getElementById('ghBackupBtn').addEventListener('click', async () => {
    const token = document.getElementById('ghToken').value.trim();
    const repo = document.getElementById('ghRepo').value.trim();
    if (!token || !repo) { showStatus('ghStatus', '请填写 Token 和仓库名', false); return; }
    showStatus('ghStatus', '备份中...', null);

    try {
      // 获取所有 storage 数据
      const allData = await chrome.storage.local.get(null);
      const files = {};
      for (const [k, v] of Object.entries(allData)) {
        if (k === 'state') continue; // 跳过运行时状态
        files[k] = v;
      }

      // 逐个文件上传到 GitHub
      let count = 0;
      for (const [name, content] of Object.entries(files)) {
        const path = `chrome-ext-data/${name}.json`;
        const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(content, null, 2))));

        // 检查文件是否已存在（获取 SHA 用于更新）
        let sha = null;
        const existResp = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
          headers: { 'Authorization': `token ${token}`, 'User-Agent': 'RestReminder-Extension' },
        });
        if (existResp.ok) {
          const existData = await existResp.json();
          sha = existData.sha;
        }

        const body = { message: `backup: ${name}`, content: encoded };
        if (sha) body.sha = sha;

        const resp = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
          method: 'PUT',
          headers: { 'Authorization': `token ${token}`, 'User-Agent': 'RestReminder-Extension', 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (resp.ok) count++;
      }
      showStatus('ghStatus', `✓ 已备份 ${count} 个文件`, true);
    } catch (e) {
      showStatus('ghStatus', `✗ ${e.message}`, false);
    }
  });

  // GitHub 恢复
  document.getElementById('ghRestoreBtn').addEventListener('click', async () => {
    const token = document.getElementById('ghToken').value.trim();
    const repo = document.getElementById('ghRepo').value.trim();
    if (!token || !repo) { showStatus('ghStatus', '请填写 Token 和仓库名', false); return; }
    if (!confirm('确定恢复数据？当前数据将被覆盖。')) return;
    showStatus('ghStatus', '恢复中...', null);

    try {
      // 列出 chrome-ext-data 目录
      const listResp = await fetch(`https://api.github.com/repos/${repo}/contents/chrome-ext-data`, {
        headers: { 'Authorization': `token ${token}`, 'User-Agent': 'RestReminder-Extension' },
      });
      if (!listResp.ok) throw new Error(`目录不存在或无权限 (HTTP ${listResp.status})`);
      const files = await listResp.json();

      let count = 0;
      for (const file of files) {
        if (!file.name.endsWith('.json')) continue;
        const dataResp = await fetch(file.download_url);
        const content = await dataResp.json();
        const key = file.name.replace('.json', '');
        await chrome.storage.local.set({ [key]: content });
        count++;
      }
      showStatus('ghStatus', `✓ 已恢复 ${count} 个文件，刷新页面生效`, true);
    } catch (e) {
      showStatus('ghStatus', `✗ ${e.message}`, false);
    }
  });

  // 重置
  document.getElementById('resetBtn').addEventListener('click', () => {
    if (confirm('确定重置今日数据？')) {
      chrome.runtime.sendMessage({ action: 'reset' }, () => alert('已重置'));
    }
  });
  document.getElementById('clearAllBtn').addEventListener('click', () => {
    if (confirm('确定清除所有数据？此操作不可恢复。')) {
      chrome.storage.local.clear(() => { alert('已清除'); location.reload(); });
    }
  });
});

function saveSettings() {
  const settings = {
    focusMinutes: parseInt(document.getElementById('focusMinutes').value) || 60,
    restMinutes: parseInt(document.getElementById('restMinutes').value) || 5,
    eyeRestInterval: parseInt(document.getElementById('eyeRestInterval').value) || 20,
    notificationsEnabled: document.getElementById('notificationsEnabled').checked,
    feishuEnabled: document.getElementById('feishuEnabled').checked,
    mailEnabled: document.getElementById('mailEnabled').checked,
    mailTo: document.getElementById('mailTo').value.trim(),
    ghToken: document.getElementById('ghToken').value.trim(),
    ghRepo: document.getElementById('ghRepo').value.trim(),
  };
  chrome.storage.local.set({ settings });
}

function showStatus(id, msg, ok) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
}
