# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：品牌名「⚡ 精力管理」。动态计时（45-60min，根据键盘/鼠标活动密度自动调整）+ 活动检测（5分钟无操作自动暂停）+ 20-20-20 护眼提醒 + 每日目标锚点 + 每小时快速自评复盘 + 请辨金句休息轮播 + 连续打卡里程碑金句奖励 + B站收藏夹随机视频 + 电池监控 + 22:00 倒计时 + 数据本地持久化 + 跨重启状态续接。深色奢华主题，2×2 卡片网格布局。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（开源版）
design-preview.html           — 最新UI设计稿（frontend-design）
rest-reminder-pro/            — Pro版（订阅制）
  backend.py                  — Supabase客户端 + 订阅验证
  user_settings.py            — 用户可配置项（B站收藏夹/提醒视频）
  pro_features/__init__.py    — Pro功能门控（云同步/统计/导出/主题）
  rest_reminder.py            — 主程序（接入Pro功能）
  wechat-pay.jpg              — 微信收款码
RestReminder.spec             — 开源版打包配置
RestReminderPro.spec          — Pro版打包配置
```

## 主要功能（v3.2+ 新增）
- **活动密度感知**：`GetLastInputInfo` 每15秒检查空闲，idle>5min自动暂停，连续活跃10min+缩间隔到45min
- **每日目标锚点**：启动时点击顶部「🎯 点我设今日目标」，持久到 `.goal.json`
- **请辨金句模式**：右键菜单→提醒方式→💡 请辨金句，15条金句每日不重复
- **每小时复盘**：倒计时结束后弹出 QInputDialog 自评 1-5⭐
- **打卡里程碑**：1/3/7/14/30/60/90/365 天显示不同金句（`STREAK_MILESTONE`）
- **跨重启续接**：`.app_state.json` 每30秒存 timer_state、_activity_interval、break_minutes 等

## 持久化文件
- `.daily_log.json` — 每日学习/电脑/休息数据
- `.app_state.json` — 计时器状态（每30秒自动保存）
- `.computer_usage.json` — 电脑使用计数
- `.goal.json` — 今日目标
- `.streak.json` — 连续打卡
- `.settings.json` — 提醒方式设置
- `.stats_history.json` — 30天历史统计

## 订阅系统
- **Supabase 表**：`subscriptions`（device_id + expires_at + active + referral_code）
- **推荐返利**：`referrals` 表（referrer_device + referred_device + reward_granted）
- **激活流程**：用户付钱 → 发 device_id → 后台插记录 → 重启app → Pro生效
- **三级验证**：Supabase云端 → 本地缓存 → 24h离线宽容

## 构建
```bash
# 开源版
pyinstaller RestReminder.spec
# Pro版
pyinstaller RestReminderPro.spec
# 输出：dist/RestReminder.exe 或 dist/RestReminderPro.exe
```

## 踩坑记录（必读）
- **SingleInstanceChecker 必须模块级生命周期**：放在 main() 作为局部变量会 GC 回收导致锁文件清理异常
- **WindowsApps pythonw.exe 是 Store 代理**：文件 < 100KB，会启动双实例
- **注册表自启动指向主程序**：崩溃后用户手动重启，比看门狗更可靠
- **opencli 发布小红书需要 180s 超时**：`OPENCLI_BROWSER_COMMAND_TIMEOUT=180000`

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可
