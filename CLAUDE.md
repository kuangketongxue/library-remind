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
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，AI 学习分析。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（~3340行，含所有 UI + 逻辑）
storage.py                    — 统一 JSON 存储层（JSONStore 类）
tray_card.py                  — 托盘弹出卡片
rest-reminder-pro/            — AI 分析模块
  pro_features/__init__.py    — AI 报告生成（agnes-2.0-flash，日报/周报/月报/季报/年报）
  backend.py                  — 已废弃（原 Supabase 订阅验证）
RestReminder.spec             — PyInstaller 配置（含 hiddenimports=['storage']）
D:\rest-reminder-site\        — 官网 Next.js 源码（纯英文路径避坑）
dist/RestReminder.exe         — 打包 exe
```

## AI 学习分析
- **无需订阅**：AI 报告直接可用，无 Pro 验证
- **主 API**：SenseNova agnes-2.0-flash（`token.sensenova.cn/v1`）
- **备用 API**：Agnes agnes-2.0-flash（`apihub.agnes-ai.com/v1`），自动降级链 + 指数退避
- **TTS 语音**：StepFun stepaudio-2.5-tts（`api.stepfun.com/v1/audio/speech`），异步线程播放
- **功能**：日报/周报/月报/季报/年报
- **缓存**：`.report_cache/` 目录，每个报告类型一个 JSON
- **数据源**：`.stats_history.json` + `.review_log.json`
- **报告生成异步化**：子线程调用 generate_report，QTimer.singleShot 回主线程更新 UI，防止阻塞崩溃

## 持久化文件
`.daily_log.json` · `.app_state.json` · `.computer_usage.json` · `.goal.json` · `.streak.json` · `.settings.json` · `.stats_history.json` · `.review_log.json`

## 构建 & 部署
```bash
pyinstaller RestReminder.spec
# 官网（纯英文路径下构建，否则Turbopack panic）
cd D:\rest-reminder-site && npm run build
CLOUDFLARE_API_TOKEN="cfut_..." wrangler pages deploy "D:\rest-reminder-site\out" --project-name "rest-reminder-app" --commit-dirty=true
```

## 搜索规则
见全局 `~/.claude/CLAUDE.md`（firecrawl×3 + tavily×2 + zhihu + global + opencli 并行）。

## 踩坑记录（必读）
- **子目录模块需显式加入 sys.path**：`rest-reminder-pro/` 等子目录不会被 Python 自动发现，启动时 `sys.path.insert(0, subdir)`（2026-06-20）
- **setWindowFlags 必须在 setGeometry 之前**：`FramelessWindowHint` 重建窗口导致几何尺寸丢失，窗口变 48x48（2026-06-20）
- **WA_DeleteOnClose 后操作 C++ 对象**：关闭后 C++ 对象销毁，_clear_tab 用 `sip.isdeleted()` 检查，_refresh_active_tab 加 `AttributeError` catch（2026-06-20）
- **读数据时不要写文件**：UI 展示方法不应触发 save_daily_stats() 写入（2026-06-20）
- **Next.js 16 + 中文路径**：Turbopack panic → 必须纯英文路径（2026-06-19）
- **CF Pages 25MB 限制**：部署前删 out/ 中 RestReminder.exe（2026-06-19）
- **except Exception: pass 是反模式**：必须至少加 log，唯一允许 pass 的是 WA_DeleteOnClose 后的 RuntimeError（2026-06-20）
- **状态机新状态三连更新**：新增状态时同步改 `_BTN_CONFIG` + `_handle_*` 方法 + 主循环路由分支（2026-06-21）
- **PyQt 数值 API 类型安全**：`setValue()`/`setMaximum()` 只接受 int，float `//` 地板除返回 float，必须显式 `int()`（2026-06-21）

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不向 GitHub 推送 rest-reminder-pro/（含 Agnes AI key）
- 不区分 Pro/普通用户，所有功能直接可用（2026-06-20）
- 不把 Pro 收费逻辑写在代码里，收费功能以后单独加（2026-06-20）
