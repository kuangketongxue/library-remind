# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，Pro 版 AI 分析 19.9元/月。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（开源版·~3300行）
rest-reminder-pro/            — Pro版（闭源·gitignored·含 AI key）
  pro_features/__init__.py    — AI 分析 + 日报/周报/月报/季报/年报
  backend.py                  — Supabase 订阅验证 + 设备指纹
RestReminder.spec             — 开源版 PyInstaller 配置
RestReminderPro.spec          — Pro版 PyInstaller 配置
D:\rest-reminder-site\        — 官网 Next.js 源码（纯英文路径避坑）
dist/RestReminder.exe         — 打包 exe
```

## 订阅系统（2026-06-18 更新）
- **Pro 仅 AI 分析**：Agnes agnes-2.0-flash API，日报/周报/月报/季报/年报
- **无限免期**：付费即用，19.9元/月
- **验证**：Supabase `subscriptions` 表（device_id + clerk_user_id + expires_at + active）
- **设备绑定**：网站 /account → 输入 device_id → Supabase 写入（每账号限 2 台）
- **Clerk**：已配置 `pk_test_...`，WARP 阻断时降级 Supabase Auth
- **RLS**：已启用
- **缓存**：本地 `.pro_cache.json`，1h 过期

## 持久化文件
`.daily_log.json` · `.app_state.json` · `.computer_usage.json` · `.goal.json` · `.streak.json` · `.settings.json` · `.stats_history.json` · `.review_log.json`

## 构建
```bash
# 开源版（中文路径问题已解：先 rm -rf build/__pycache__/ 再跑）
pyinstaller RestReminder.spec
# Pro版
pyinstaller RestReminderPro.spec
```

## 官网部署
```bash
# 必须在纯英文路径下构建（中文→Turbopack panic）
cd D:\rest-reminder-site
npm run build
# 用 Cloudflare API Token 部署
CLOUDFLARE_API_TOKEN="cfut_..." wrangler pages deploy "D:\rest-reminder-site\out" --project-name "rest-reminder-app" --commit-dirty=true
```

## 搜索规则
5 源并行：firecrawl × 3 + tavily × 2 + zhihu + global + opencli。额度用完自动跳过不永久停用。

## 踩坑记录（必读）
- **Next.js 16 + 中文路径**：Turbopack panic `start byte index...` → 必须纯英文路径
- **CF Pages 25MB 限制**：部署前删 out/ 中 RestReminder.exe
- **Clerk 静态导出**：不能用 `@clerk/nextjs` 服务端组件 → 用 `@clerk/clerk-react` 纯客户端
- **SingleInstanceChecker 模块级生命周期**：放 main() 局部变量会被 GC
- **B站 test 按钮超时**：5s 超时 + 兜底方案，WARP 下会提示网络限制
- **21 处 `except Exception:`** 添加了 `log.error` 但仍有少数 stateless 的 continue 未加日志

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不向 GitHub 推送 rest-reminder-pro/（含 Agnes AI key）