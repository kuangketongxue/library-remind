# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，AI 学习分析。

## 技术栈
Python 3.14+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（4326行，含所有 UI + 逻辑）
storage.py                    — 统一 JSON 存储层（JSONStore 类）
RestReminder.spec             — PyInstaller 配置（含 hiddenimports=['storage']）
产品规格-v4.3.md              — v4.3 完整产品规格
```

## AI 学习分析
- **无需付费**：AI 报告直接可用
- **主 API**：SenseNova `sensenova-6.7-flash-lite`（`token.sensenova.cn/v1/chat/completions`）
- **备用 API**：Agnes `agnes-2.0-flash`（`apihub.agnes-ai.com/v1/chat/completions`），自动降级链 + 指数退避
- **TTS 语音**：StepFun `stepaudio-2.5-tts`（`api.stepfun.com/v1/audio/speech`），异步线程播放
- **功能**：日报/周报/月报/季报/年报
- **缓存**：`.report_cache/` 目录，每个报告类型一个 JSON
- **数据源**：`.stats_history.json` + `.review_log.json`

## 持久化文件
`.daily_log.json` · `.app_state.json` · `.goal.json` · `.streak.json` · `.settings.json` · `.stats_history.json` · `.review_log.json`

## 构建 & 部署
```bash
pyinstaller RestReminder.spec
```

## 搜索规则
见全局 `~/.claude/CLAUDE.md`（firecrawl×3 + tavily×2 + zhihu + global + opencli 并行）。

## 踩坑记录（必读）
- **子目录模块需显式加入 sys.path**：嵌套子目录（如 `rest-reminder-site/`）不会被 Python 自动发现，启动时 `sys.path.insert(0, subdir)`（2026-06-20）
- **setWindowFlags 必须在 setGeometry 之前**：`FramelessWindowHint` 重建窗口导致几何尺寸丢失，窗口变 48x48（2026-06-20）
- **WA_DeleteOnClose 后操作 C++ 对象**：关闭后 C++ 对象销毁，_clear_tab 用 `sip.isdeleted()` 检查，_refresh_active_tab 加 `AttributeError` catch（2026-06-20）
- **读数据时不要写文件**：UI 展示方法不应触发 save_daily_stats() 写入（2026-06-20）
- **Next.js 16 + 中文路径**：Turbopack panic → 必须纯英文路径（2026-06-19）
- **CF Pages 25MB 限制**：部署前删 out/ 中 RestReminder.exe（2026-06-19）
- **except Exception: pass 是反模式**：必须至少加 log，唯一允许 pass 的是 WA_DeleteOnClose 后的 RuntimeError（2026-06-20）
- **状态机新状态三连更新**：新增状态时同步改 `_BTN_CONFIG` + `_handle_*` 方法 + 主循环路由分支（2026-06-21）
- **PyQt 数值 API 类型安全**：`setValue()`/`setMaximum()` 只接受 int，float `//` 地板除返回 float，必须显式 `int()`（2026-06-21）
- **log 中不要用 [LINE NNN] 标记**：代码移动后行号立刻过时，用描述性消息替代（如 `"[单实例] 解锁失败: {e}"`）（2026-06-21）
- **centralized utility 迁移必须一次性完成**：创建 `open_url()` 后 grep 所有 `webbrowser.open`/`ShellExecuteW` 调用点，全部替换，不留绕过（2026-06-21）
- **UI 重构后审计 settings 数据流**：每个 settings key 的写入点必须有对应的读取点，否则设置是摆设（2026-06-21）

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不把收费逻辑写在代码里（v4.4 全免费）
- 活动密度感知已删除，不在任何文档/代码中引用（2026-06-23）
