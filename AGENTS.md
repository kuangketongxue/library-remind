# 休息提醒 — AGENTS.md

## 项目概述
PyQt5 桌面挂件：浮球（⏰ 60×60，点击弹出倒计时+学习时长+开始/暂停）+ 主面板（560×480 CC Switch 风格，5 tab：今日/AI报告/趋势/关于）。60 分钟学习 → 5 分钟请辨倒计时 → 5 分钟休息 → 固定 B 站收藏夹。AI 学习分析 + 趋势分析 + 复盘 1-5⭐。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil / Win32 API (ctypes)

## 关键文件
```
rest_reminder.py        — 主程序（~3100行，含所有 UI + 逻辑）
storage.py              — 统一 JSON 存储层（JSONStore 类）
tray_card.py            — 托盘弹出卡片（已弃用，保留兼容）
rest-reminder-pro/      — AI 分析模块
  pro_features/__init__.py — AI 报告生成（agnes-2.0-flash，日报/周报/月报/季报/年报）
RestReminder.spec       — PyInstaller 配置（含 hiddenimports=['storage']）
D:\rest-reminder-site\  — 官网 Next.js 源码（纯英文路径避坑）
dist/RestReminder.exe   — 打包 exe
产品规格-v4.3.md        — v4.3 完整产品规格（计时规则/URL/功能清单）
```

## 计时规则（v4.3，核心变更）
- 固定 60 分钟学习 → 最后 5 分钟请辨浮层 → 5 分钟休息（固定）
- 普通休息后打开收藏夹：`https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0`
- 每 3 轮后（第 3/6/9...轮）打开护眼视频：`https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click`
- 休息期间弹出复盘 1-5⭐ 选择题
- 状态机：idle → running → resting → idle（循环）
- **已删除**：电脑使用 3 小时周期、20-20-20 护眼浮窗、活动密度感知/空闲自动暂停、随机视频选择

## 关键配置位置
| 配置 | 位置 | 默认值 |
|------|------|--------|
| 学习间隔 | 固定 60 分钟 | 无动态调整 |
| 休息时长 | 固定 5 分钟 | `_handle_resting` |
| 收藏夹 URL | `_handle_resting` | 固定 URL（非随机） |
| 护眼视频 URL | `_handle_resting` round % 3 == 0 | BV14Y4y1N7PW |
| 请辨金句 | `_pick_quote()` | quotes_store |
| 复盘分数 | `.review_log.json` | 1-5⭐ |
| 学习时长 | `.daily_log.json` | LocalSync |
| 窗口尺寸 | `init_ui()` | 560×480 |
| 浮球尺寸 | `FloatingBall` | 60×60 |

## 运行和验证
```bash
# 启动主程序
python rest_reminder.py --silent

# 验证进程
tasklist | findstr "python.exe"

# 杀掉进程
taskkill /F /IM python.exe
```

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
