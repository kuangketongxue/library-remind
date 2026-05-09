# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：手动开始 60 分钟计时 + 暂停/继续 + 休息时自动打开 B 站视频 + 电池监控。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil

## 关键文件
```
rest_reminder.py        — 主程序（所有逻辑都在这一个文件）
cute_icon.png / .ico    — 托盘和任务栏图标
requirements.txt        — 依赖：PyQt5, requests, psutil
一键安装.bat             — 安装+自启动+启动（推荐用户入口）
```

## 关键配置位置（rest_reminder.py）
| 配置 | 位置 | 默认值 |
|------|------|--------|
| 提醒间隔 | `self.interval_minutes` | 60 分钟 |
| 收藏夹 ID | `get_bilibili_videos()` 内 `fid` | 3648313921 |
| 用户 ID | `get_bilibili_videos()` 内 `mid` | 529362421 |
| 窗口尺寸 | `init_ui()` 内 `widget_width/widget_height` | 340×370 |
| 倒计时范围 | `update_display()` 内 `start_minutes/end_minutes` | 4:30~22:00 |
| 学习目标时长 | `study_progress_bar.setMaximum` | 14（14小时） |
| 飞书轮询间隔 | `setup_timer()` 内 `self.feishu_timer.start` | 30000ms（30秒） |
| 飞书 base token | 顶部 `FEISHU_BASE_TOKEN` | DcJzbLadCaGbGws2ZekchGHhnVe |
| 飞书表 ID | 顶部 `FEISHU_TABLE_ID` | tbl9DT9qniE63BH7 |
| 飞书视图名 | 顶部 `FEISHU_VIEW_NAME` | 时长 |
| 开机自启动 | `__init__()` 内 `self.set_autostart(True)` | 启动时自动注册 HKCU\...\Run |
| 自启动注册表键 | `RestReminder` | HKCU\Software\Microsoft\Windows\CurrentVersion\Run |
| 电池轮询间隔 | `update_display()` 内 `_battery_tick` 计数器 | 每 15 秒 |
| 计时器状态机 | `self.timer_state` | idle → running → paused（手动开始/暂停） |

## 运行和验证
```bash
# 启动（后台，无控制台）
pythonw rest_reminder.py

# 启动（调试，有控制台输出）
python rest_reminder.py

# 验证进程是否在跑
wmic process where "name='pythonw.exe' or name='python.exe'" get CommandLine,ProcessId 2>/dev/null | grep rest_reminder

# 杀掉进程
taskkill //PID <pid> //F
```

## 改完代码后必须做的
1. 杀掉旧进程：`taskkill //PID <pid> //F`
2. 启动新进程：`start "" pythonw rest_reminder.py`（从项目目录执行）
3. 验证新进程 PID 已出现

## 禁止事项
- 不创建庆祝/确认类临时文件（🎉✅🎊命名的 .txt/.md）
- 不写重复的修复报告/总结——改 README changelog 即可
- 任务完成时改已有文档，不新建"已完成"文件

## 文档
- README.md — 用户文档（功能、安装、FAQ）
- 使用说明_完整版.txt — 详细操作指南
- 修复说明.md / 单实例功能说明.md / 后台运行说明.md — 技术细节
