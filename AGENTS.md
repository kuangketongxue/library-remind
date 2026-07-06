# 休息提醒 — AGENTS.md

## 项目概述
PyQt5 桌面挂件：浮球（⚡ 60×60 可拖动，点击打开主界面）+ 主面板（960×680，5 tab：今日/AI报告/趋势/设置/关于）。60 分钟学习 → 5 分钟请辨倒计时 → 复盘 1-100 分 → 5 分钟休息 → 固定 B 站收藏夹。AI 学习分析 + 趋势分析（单柱图+tooltip+时段评分热力图）。

## 技术栈
Python 3.14+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py        — 主程序（~8200行，含所有 UI + 逻辑）
storage.py              — 统一 JSON 存储层（JSONStore 类）
tray_card.py            — 浮动托盘卡片组件（替代原生 QMenu）
feishu_calendar.py      — 飞书日程集成
RestReminder.spec       — PyInstaller 配置（hiddenimports=['storage','tray_card','feishu_calendar']）
CHANGELOG.md            — 更新日志
```

## 计时规则（v5.0，固定循环）
- 固定 60 分钟学习 → 最后 5 分钟请辨浮层 → 5 分钟休息（固定）
- 普通休息后打开收藏夹：`https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0`
- 每 3 轮后（第 3/6/9...轮）打开护眼视频：`https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click`
- 休息期间弹出复盘 1-100分（学科 + 标签 + 评分）
- 状态机：idle → running → paused → resting → idle（4 态循环）
- **已删除**：电脑使用 3 小时周期、活动密度感知/空闲自动暂停、随机视频选择、双柱图、饼图
- **20-20-20 护眼**：每20分钟轻量浮窗，不打断学习

## 关键配置位置
| 配置 | 位置 | 默认值 |
|------|------|--------|
| 学习间隔 | 固定 60 分钟 | 无动态调整 |
| 休息时长 | 固定 5 分钟 | `_handle_resting` |
| 收藏夹 URL | `_handle_resting` | 固定 URL（非随机） |
| 护眼视频 URL | `_handle_resting` round % 3 == 0 | BV14Y4y1N7PW |
| 请辨金句 | `_pick_quote()` | quotes_store |
| 复盘分数 | `.review_log.json` | 1-100分 |
| 学习时长 | `.daily_log.json` | LocalSync |
| 窗口尺寸 | `init_ui()` | 960×680 |
| 浮球尺寸 | `FloatingBall` | 60×60，可拖动 |

## 运行和验证
```bash
# 启动主程序（必须用 Python 3.14，vendor 内 .pyd 按其 ABI 编译）
# 自动启动/后台运行用 pythonw.exe（无控制台窗口）
C:\Python314\pythonw.exe rest_reminder.py --silent

# 前台调试用 python.exe
C:\Python314\python.exe rest_reminder.py

# 验证进程
tasklist | findstr "python"

# 杀掉进程
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
```

## 关键踩坑
- **Python 3.14 兼容**：`from PyQt5 import sip`（`import sip` 在 3.14 失败），`QToolTip` 从 QtWidgets 导入
- **vendor 路径**：`rest_reminder.py` 顶部自动把 `vendor/` 加到 `sys.path`，开箱即用无需 `pip install`；仅 Python 3.14 兼容
- **`python` 命令陷阱**：PATH 里 `python` 可能解析到其他版本，启动会报 `ImportError: cannot import name 'sip'`，必须用 `C:\Python314\python.exe`
- **_md_to_html 是模块级函数**：不在任何类中，`RestReminderWidget` 和 `FloatingBall` 都可直接调用
- **Edit 工具中文 TSX**：含中文的 TSX 文件 Edit 静默失败 → 改用 Write 工具全量重写
- **CF Pages 部署**：`cd rest-reminder-site && npm run build && wrangler pages deploy out --project-name=crazy-rest-reminder --branch=main`（含 Functions 部署；需要 `CLOUDFLARE_API_TOKEN` 环境变量；GitHub Actions 只部署静态文件，Functions 需手动 wrangler 部署；构建后自动运行 fix-routes.js 修复 Cloudflare Pages 路由）
- **浮球 popup 空白**：`_show_info_popup()` 默认文字刷新在 `if popup is None:` 块内，关闭后再点击浮球打开时跳过刷新。默认文字 + `_update_popup_text()` 必须移到块外，每次显示都执行
- **Next.js 构建缓存**：`.next` 缓存导致 Turbopack 报错时行号与实际文件不符 → `rm -rf .next out node_modules/.cache` 清缓存重建
- **git push 认证**：WARP 环境下用 `git config credential.helper store` + `~/.git-credentials` 文件
- **Windows 任务栏图标**：直接 `python.exe` 启动会显示 Python 图标；需创建 `.lnk` 快捷方式绑定 `cute_icon.ico`，或用 PyInstaller 打包 EXE
- **PyQt5 多实例防护**：用 `kernel32.CreateMutexW + GetLastError==183`，原子操作，崩溃自动释放，名称用 `Global\` 前缀（v5.4.0，2026-06-29）
- **Win11 任务栏图标丢失**：`FramelessWindowHint + WindowStaysOnTopHint` 导致图标消失；`showEvent` 中用 ctypes 设 `WS_EX_APPWINDOW`、去 `WS_EX_TOOLWINDOW`（v5.4.0）
- **SenseNova 推理模型**：`sensenova-6.7-flash-lite` content 可能为空，回复在 `reasoning` 字段，需 `max_tokens>=4096` 并 fallback（v5.4.0）

## 改完代码后必须做的
1. 杀掉旧进程：`taskkill /F /IM python.exe`
2. 语法检查：`C:\Python314\python.exe -c "import py_compile; py_compile.compile('rest_reminder.py')"`
3. 启动主程序：`C:\Python314\python.exe rest_reminder.py --silent`
4. 验证新进程 PID 已出现，无 crash.log

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复修复报告——改 CHANGELOG.md 即可
- 不向 GitHub 推送 rest-reminder-pro/（含 Agnes AI key）
- 不区分 Pro/普通用户，所有功能直接可用
- 不把 Pro 收费逻辑写在代码里

## 文档
- CLAUDE.md — AI 开发规则 + 踩坑记录
- docs/ARCHITECTURE.md — 架构/状态机/设计系统
- CHANGELOG.md — 更新日志
