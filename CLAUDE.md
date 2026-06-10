# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：60 分钟计时（自动循环）+ 20-20-20 护眼提醒（每 20 分钟轻量浮窗提示看远处）+ 暂停/继续 + 每小时随机打开 B 站收藏夹视频 + 每 3 小时打开护眼视频 + 电池监控 + 22:00 倒计时 + 数据本地持久化。绿色小浮球：点击显示/隐藏主窗口，可拖动。看门狗守护：watchdog.py 监控主进程，崩溃自动重启，开机自启动指向看门狗。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil

## 关键文件
```
rest_reminder.py              — 主程序（开源版）
watchdog.py                   — 看门狗进程
rest-reminder-pro/            — Pro版（订阅制）
  backend.py                  — Supabase客户端 + 订阅验证
  user_settings.py            — 用户可配置项（B站收藏夹/提醒视频）
  pro_features/__init__.py    — Pro功能门控（云同步/统计/导出/主题）
  rest_reminder.py            — 主程序（接入Pro功能）
  wechat-pay.jpg              — 微信收款码
RestReminder.spec             — 开源版打包配置
RestReminderPro.spec          — Pro版打包配置
```

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
- **SingleInstanceChecker 必须模块级生命周期**：放在 main() 作为局部变量会 GC 回收导致 watchdog 误判重启
- **WindowsApps pythonw.exe 是 Store 代理**：文件 < 100KB，会启动双实例
- **注册表自启动必须指向 watchdog.py**：指向 rest_reminder.py 则崩溃后无守护
- **opencli 发布小红书需要 180s 超时**：`OPENCLI_BROWSER_COMMAND_TIMEOUT=180000`

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可
