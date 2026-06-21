# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，AI 学习分析。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（~3100行，含所有 UI + 逻辑）
storage.py                    — 统一 JSON 存储层（JSONStore 类）
tray_card.py                  — 托盘弹出卡片
rest-reminder-pro/            — AI 分析模块
  pro_features/__init__.py    — AI 报告生成（agnes-2.0-flash，日报/周报/月报/季报/年报）
RestReminder.spec             — PyInstaller 配置（含 hiddenimports=['storage']）
产品规格-v4.3.md              — v4.3 完整产品规格
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
- **log 中不要用 [LINE NNN] 标记**：代码移动后行号立刻过时，用描述性消息替代（如 `"[单实例] 解锁失败: {e}"`）（2026-06-21）
- **centralized utility 迁移必须一次性完成**：创建 `open_url()` 后 grep 所有 `webbrowser.open`/`ShellExecuteW` 调用点，全部替换，不留绕过（2026-06-21）
- **UI 重构后审计 settings 数据流**：每个 settings key 的写入点必须有对应的读取点，否则设置是摆设（2026-06-21）

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不向 GitHub 推送 rest-reminder-pro/（含 Agnes AI key）
- 不区分 Pro/普通用户，所有功能直接可用（2026-06-20）
- 不把 Pro 收费逻辑写在代码里，收费功能以后单独加（2026-06-20）
