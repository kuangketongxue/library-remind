// ═══ 精力管理 — Options 逻辑 ═══

document.addEventListener('DOMContentLoaded', () => {
  // 加载设置
  chrome.storage.local.get(['settings'], (res) => {
    const s = res.settings || {};
    document.getElementById('focusMinutes').value = s.focusMinutes || 60;
    document.getElementById('restMinutes').value = s.restMinutes || 5;
    document.getElementById('eyeRestInterval').value = s.eyeRestInterval || 20;
    document.getElementById('notificationsEnabled').checked = s.notificationsEnabled !== false;
  });

  // 保存设置（输入变化时自动保存）
  const inputs = document.querySelectorAll('input');
  inputs.forEach((input) => {
    input.addEventListener('change', saveSettings);
  });

  // 重置今日数据
  document.getElementById('resetBtn').addEventListener('click', () => {
    if (confirm('确定重置今日数据？')) {
      chrome.runtime.sendMessage({ action: 'reset' }, () => {
        alert('已重置');
      });
    }
  });

  // 清除所有数据
  document.getElementById('clearAllBtn').addEventListener('click', () => {
    if (confirm('确定清除所有数据？此操作不可恢复。')) {
      chrome.storage.local.clear(() => {
        alert('已清除');
        location.reload();
      });
    }
  });
});

function saveSettings() {
  const settings = {
    focusMinutes: parseInt(document.getElementById('focusMinutes').value) || 60,
    restMinutes: parseInt(document.getElementById('restMinutes').value) || 5,
    eyeRestInterval: parseInt(document.getElementById('eyeRestInterval').value) || 20,
    notificationsEnabled: document.getElementById('notificationsEnabled').checked,
  };
  chrome.storage.local.set({ settings });
}
