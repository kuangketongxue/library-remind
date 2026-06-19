# 休息提醒 — CLAUDE.md

## 产品定位（2026-06-19 竞品调研更新）

### 竞品格局
| 类型 | 代表 | 做法 | 收费 |
|------|------|------|------|
| 大厂 | Win11 Focus Sessions / Apple Focus / Google Digital Wellbeing | 系统级番茄钟+通知屏蔽 | 免费（随系统） |
| 独立产品 | Forest / TITA / Just Focus | 游戏化锁机 + 极简设计 | 免费基础+内购 |
| 播放器 | Biu/BBPlayer | B站收藏夹自动播放 | 开源免费 |

**关键发现**：没有竞品同时做"休息提醒 + B站收藏夹播放 + AI 学习分析"三合一。

### 核心壁垒
- 大厂做系统集成（做不了）
- 独立产品只做单一功能（想不到）
- 我们三合一 = 世界上没有第二款

### 差异化定位
> **"学习休息的娱乐伴侣"** — 专注累了自动播放你收藏的知识视频，AI 分析你的学习节奏。

- 大厂：帮你屏蔽干扰 → 我们：帮你引导注意力
- 番茄钟：强制休息 → 我们：休息 = 看收藏夹里的好内容
- 专注工具：孤立计时器 → 我们：计时器 + 内容 + AI 洞察

### 增长路径
- 小红书/知乎发「复读生的一天」内容 → 自然带出工具（trait-016）
- 开源 + GitHub 存在感 → 技术社区传播
- B站收藏夹功能 → B站用户直接共鸣

## 项目概述
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，Pro 版 AI 分析。

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

## 构建 & 部署
```bash
# 开源版
pyinstaller RestReminder.spec
# Pro版
pyinstaller RestReminderPro.spec
# 官网（纯英文路径下构建，否则Turbopack panic）
cd D:\rest-reminder-site && npm run build
CLOUDFLARE_API_TOKEN="cfut_..." wrangler pages deploy "D:\rest-reminder-site\out" --project-name "rest-reminder-app" --commit-dirty=true
```

## 搜索规则
见全局 `~/.claude/CLAUDE.md`（firecrawl×3 + tavily×2 + zhihu + global + opencli 并行）。

## 踩坑记录（必读）
- **Next.js 16 + 中文路径**：Turbopack panic `start byte index...` → 必须纯英文路径
- **CF Pages 25MB 限制**：部署前删 out/ 中 RestReminder.exe
- **Clerk 静态导出**：不能用 `@clerk/nextjs` 服务端组件 → 用 `@clerk/clerk-react` 纯客户端
- **SingleInstanceChecker 模块级生命周期**：放 main() 局部变量会被 GC
- **B站 test 按钮超时**：5s 超时 + 兜底方案，WARP 下会提示网络限制
- **21 处 `except Exception:`** 添加了 `log.error` 但仍有少数 stateless 的 continue 未加日志
- **`self.autostart_action` 未定义**：调用 `self.XXX` 前先 grep 确认属性存在（2026-06-19）
- **`# 已移除UI` 残留**：v4.0 重构时注释了 16 处旧 UI 代码，应直接删除不注释（2026-06-19）
- **DNS error flag 在方法内重置**：`get_bilibili_videos()` 开头重置 `_bilibili_dns_error_logged`，应在 `__init__` 中初始化一次（2026-06-19）
- **`_load_json` 跨类共享**：无状态工具函数提取到模块级，不要放在某个类内部（2026-06-19）

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不向 GitHub 推送 rest-reminder-pro/（含 Agnes AI key）