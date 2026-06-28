# 休息提醒 — AGENTS.md

## 项目概述
PyQt5 桌面挂件：浮球（⚡ 60×60 可拖动，点击打开主界面）+ 主面板（960×680，5 tab：今日/AI报告/趋势/设置/关于）。60 分钟学习 → 5 分钟请辨倒计时 → 复盘 1-100 分 → 5 分钟休息 → 固定 B 站收藏夹。AI 学习分析 + 趋势分析（单柱图+tooltip+时段评分热力图）。

## 技术栈
Python 3.14+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py        — 主程序（~4737行，含所有 UI + 逻辑）
storage.py              — 统一 JSON 存储层（JSONStore 类）
RestReminder.spec       — PyInstaller 配置（含 hiddenimports=['storage']）
CHANGELOG.md            — 更新日志
```

## 计时规则（v5.0，固定循环）
- 固定 60 分钟学习 → 最后 5 分钟请辨浮层 → 5 分钟休息（固定）
- 普通休息后打开收藏夹：`https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0`
- 每 3 轮后（第 3/6/9...轮）打开护眼视频：`https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click`
- 休息期间弹出复盘 1-100分（学科 + 标签 + 评分）
- 状态机：idle → running → resting → idle（循环）
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
# 启动主程序
python rest_reminder.py --silent

# 验证进程
tasklist | findstr "python.exe"

# 杀掉进程
taskkill /F /IM python.exe
```

## 关键踩坑
- **Python 3.14 兼容**：`from PyQt5 import sip`（`import sip` 在 3.14 失败），`QToolTip` 从 QtWidgets 导入
- **_md_to_html 是模块级函数**：不在任何类中，`RestReminderWidget` 和 `FloatingBall` 都可直接调用
- **Edit 工具中文 TSX**：含中文的 TSX 文件 Edit 静默失败 → 改用 Write 工具全量重写
- **CF Pages 部署**：`npx wrangler pages deploy out --project-name=crazy-rest-reminder`（不是 `wrangler deploy`）
- **git push 认证**：WARP 环境下用 `git config credential.helper store` + `~/.git-credentials` 文件

## 改完代码后必须做的
1. 杀掉旧进程：`taskkill /F /IM python.exe`
2. 语法检查：`python -c "import py_compile; py_compile.compile('rest_reminder.py')"`
3. 启动主程序：`python rest_reminder.py --silent`
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
- 产品规格-v4.3.md — v4.3 完整产品规格
