# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件，品牌名「⚡ 精力管理」。开源 MIT，AI 学习分析。

## 技术栈
Python 3.14+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py              — 主程序（~8200行，含所有 UI + 逻辑）
storage.py                    — 统一 JSON 存储层（JSONStore 类）
tray_card.py                  — 浮动托盘卡片组件
feishu_calendar.py            — 飞书日程集成
RestReminder.spec             — PyInstaller 配置（含 hiddenimports=['storage','tray_card','feishu_calendar']）
```

## AI 学习分析
- **无需付费**：AI 报告直接可用
- **架构**：任意 OpenAI 兼容 API + Cloudflare Worker 代理（`rest-reminder-site/functions/api/ai-proxy.js`）
- **provider 模型**：`ai_providers` 列表，priority 排序，fallback 链式尝试
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

## 核心工作原则

### 第一性原理
遇到问题时，先分解到最基本的事实和约束，从底层重新推理，而非类比既有方案或惯性做法：
- 动手前先问"这件事的本质目标是什么？有哪些隐含假设？假设是否成立？"
- 不接受"一直都这样做"作为理由——验证每个前提是否在当前上下文仍然成立
- 宁可多花时间理解根因，也不要在症状上打补丁

### 对抗性审查
每次交付代码前，主动切换到"找茬模式"攻击自己的产出：
- 至少覆盖三个维度：正确性（边界/异常/并发）、完整性（需求是否全覆盖）、健壮性（失败时有没有兜底）
- 修复前必须先验证：读实际代码、检查函数/变量名是否匹配、分类 CONFIRMED/FALSE POSITIVE 并附证据
- 发现问题直接修复，不要只列清单等用户确认；修复后再次审查，直到找不到明显缺陷

### 验证实际运行
- 代码改完必须 kill 旧进程 → 启动 → 读 crash.log → 确认 UI 可见，才能报告完成
- `crash.log` 是第一调试入口，用户报告"没变化/看不到"时第一步 `type crash.log`，不要猜
- 用户两次发相同指令 = 上次没生效信号，立即检查 crash.log 和进程状态，不要重新开发

### 穷尽方案再求助
- 用户给了多个凭证/方案时，应全部尝试再求助
- 一种方式失败应换 token/换协议/换认证方式，穷尽后再报告阻塞

## 踩坑记录（必读）
- **子目录模块需显式加入 sys.path**：嵌套子目录（如 `rest-reminder-site/`）不会被 Python 自动发现，启动时 `sys.path.insert(0, subdir)`（2026-06-20）
- **setWindowFlags 必须在 setGeometry 之前**：`FramelessWindowHint` 重建窗口导致几何尺寸丢失，窗口变 48x48（2026-06-20）
- **WA_DeleteOnClose 后操作 C++ 对象**：关闭后 C++ 对象销毁，_clear_tab 用 `sip.isdeleted()` 检查，_refresh_active_tab 加 `AttributeError` catch（2026-06-20）
- **读数据时不要写文件**：UI 展示方法不应触发 save_daily_stats() 写入（2026-06-20）
- **Next.js 16 + 中文路径**：Turbopack panic → 必须纯英文路径（2026-06-19）
- **CF Pages 25MB 限制**：部署前删 out/ 中 RestReminder.exe（2026-06-19）
- **except Exception: pass 是反模式**：必须至少加 log，唯一允许 pass 的是 WA_DeleteOnClose 后的 RuntimeError（2026-06-20）
- **Python 3.14 兼容**：`from PyQt5 import sip`（`import sip` 在 3.14 失败），`QToolTip` 从 QtWidgets 导入，`QRect` 从 QtCore 导入
- **状态机新状态三连更新**：新增状态时同步改 `_BTN_CONFIG` + `_handle_*` 方法 + 主循环路由分支（2026-06-21）
- **PyQt 数值 API 类型安全**：`setValue()`/`setMaximum()` 只接受 int，float `//` 地板除返回 float，必须显式 `int()`（2026-06-21）
- **log 中不要用 [LINE NNN] 标记**：代码移动后行号立刻过时，用描述性消息替代（如 `"[单实例] 解锁失败: {e}"`）（2026-06-21）
- **Windows 任务栏图标**：直接 `python.exe` 启动会显示 Python 图标；需创建 `.lnk` 快捷方式绑定 `cute_icon.ico`，或用 PyInstaller 打包 EXE（2026-06-28）
- **centralized utility 迁移必须一次性完成**：创建 `open_url()` 后 grep 所有 `webbrowser.open`/`ShellExecuteW` 调用点，全部替换，不留绕过（2026-06-21）
- **UI 重构后审计 settings 数据流**：每个 settings key 的写入点必须有对应的读取点，否则设置是摆设（2026-06-21）
- **PyQt5 多实例防护**：`msvcrt.locking` 文件锁有竞态（两个实例同时启动都能通过 fallback）。改用 `kernel32.CreateMutexW + GetLastError==183` 检测，原子操作无竞态，崩溃自动释放，名称用 `Global\` 前缀（2026-06-29）
- **Win11 任务栏图标 WS_EX_APPWINDOW**：`FramelessWindowHint + WindowStaysOnTopHint` 会丢失任务栏图标。修复：`showEvent` 中用 `ctypes.windll.user32` 设 `WS_EX_APPWINDOW`、去 `WS_EX_TOOLWINDOW`（2026-06-29）
- **飞书日程 CalendarManager 初始化顺序**：`CalendarManager` 必须在 `init_ui()` 前初始化，因为 `_build_general_tab` 会读 `_calendar_enabled`（2026-06-29）
- **pythonw 下 PATH 不完整**：`lark-cli` 找不到时，需用 `shutil.which` 或绝对路径 `%APPDATA%\npm\lark-cli.cmd`，不能依赖 PATH（2026-06-29）
- **popup UI 缩进陷阱**：`if widget is None:` 块只包含 widget 创建，UI 子控件（root QFrame 等）必须也在块内，否则每次 show 重建整棵树（2026-07-04）
- **import 遗漏检测**：grep `threading\.` 等调用点后必须验证对应 import 存在；crash.log 是第一发现入口（2026-07-04）
- **尊重用户指定的文件/方案**：用户说"图标用 cute_icon.png"就用 png，不要自作主张改为 .ico（具体指令不替换方案）
- **QFont 不接受 CSS 逗号分隔**：`QFont('Georgia, "Noto Serif SC", serif')` 整个字符串被当作一个字体名 → 匹配失败 → moji-bake。只传单一主字体名，fallback 留给 Qt 字体链接表（2026-07-06）
- **PyInstaller frozen 模式数据文件路径**：`os.path.dirname(__file__)` 在 frozen 模式下指向 temp 解压目录，不是 `sys._MEIPASS`。数据文件用 `sys._MEIPASS`，脚本用 `__file__`（2026-07-06）
- **Hero 背景视频不要 opacity-0 等加载**：弱网/WARP 下 onCanPlay 不触发 → 黑屏。直接设可见 + poster 占位 + onError 降级（2026-07-06）
- **AI 调用必须有本地 fallback**：所有外部 API 超时时返回降级内容（本地数据/缓存），不要把错误甩到 UI（2026-07-06）
- **改 CSS 背景色必须排查硬编码颜色**：改 `--bg` 变量后，用 grep 扫 `rgba(255,255,255` / `bg-white` / 旧 surface 色值，逐一确认新背景上对比度（2026-07-06）
- **深色背景文字用显式白色**：navbar/dark overlay/CTA banner 的文字必须 `text-white`，不依赖 `var(--fg)`（2026-07-06）
- **Next.js 预渲染不能传 onClick**：`"use client"` 页面的交互组件如果预渲染报错，提取为独立 client component 文件（2026-07-06）
- **跨项目 learnings 不混放**：不同项目的 .learnings/ 必须分别记录到各自目录，不能跨项目写入（2026-07-06）
- **发布时必须同步 VERSION 常量**：git tag / CHANGELOG / VERSION 三者必须一致，VERSION 是运行时显示的版本（2026-07-06）
- **Windows 自启动路径必须加引号**：注册表 `HKCU\...\Run` 的路径如果含空格/中文，必须用双引号包裹，否则 Windows 解析失败。优先调用 app 内置 `set_autostart()`（2026-07-06）
- **Cloudflare Pages Functions 部署**：修改 `functions/` 下代码后必须 `wrangler pages deploy` 重新部署，GitHub Actions 只部署静态文件。部署后立即 curl 测试，405/404 则等 30 秒重新部署（2026-07-06）
- **Next.js 静态导出路由问题**：`output: 'export'` 生成 `contact.html`，但 Cloudflare Pages 需要 `contact/index.html`。构建后必须运行 `fix-routes.js` 脚本复制文件到正确位置（2026-07-06）
- **官网部署后必须验证**：部署后立即 curl 测试所有关键页面（`/` `/contact` `/docs` `/pricing` `/privacy` `/terms` `/rules`）和 AI 代理（`/api/ai-proxy`），任何 404/405 立即重新部署（2026-07-06）
- **Cloudflare Pages 部署必须用 `wrangler pages deploy .`**：用 `pages-action` 只部署静态文件，Worker 会丢失。必须从项目根目录运行 `wrangler pages deploy .` 确保 Functions 一起部署（2026-07-06）

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告
- 不把收费逻辑写在代码里（v4.4 全免费）
- 活动密度感知已删除，不在任何文档/代码中引用（2026-06-23）
