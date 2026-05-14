# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：60 分钟计时（自动循环）+ 暂停/继续 + 每小时随机打开 B 站收藏夹视频 + 每 3 小时打开护眼视频 + 电池监控 +22:00 倒计时。看门狗守护：watchdog.py 监控主进程，崩溃自动重启，开机自启动指向看门狗。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil

## 关键文件
```
rest_reminder.py        — 主程序（所有逻辑都在这一个文件）
watchdog.py             — 看门狗进程（监控主进程，崩溃自动重启，CREATE_NO_WINDOW 静默）
cute_icon.png / .ico    — 托盘和任务栏图标
requirements.txt        — 依赖：PyQt5, requests, psutil
一键安装.bat             — 安装 + 自启动 + 启动看门狗（推荐用户入口）
```

## 关键配置位置
| 配置 | 位置 | 默认值 |
|------|------|--------|
| 提醒间隔 | `self.interval_minutes` | 60 分钟（自动循环） |
| 收藏夹 ID | `get_bilibili_videos()` 内 `fid` | 3648313921 |
| 用户 ID | `get_bilibili_videos()` 内 `mid` | 529362421 |
| 护眼视频 URL | `show_computer_usage_reminder()` | BV14Y4y1N7PW |
| 电脑使用周期 | `update_computer_usage()` | 每 3 小时循环提醒 |
| 窗口尺寸 | `init_ui()` 内 `widget_width/widget_height` | 340×370 |
| 倒计时范围 | `update_display()` 内 `start_minutes/end_minutes` | 4:30~22:00（倒计时模式） |
| 学习目标时长 | `study_progress_bar.setMaximum` | 14（14 小时） |
| 飞书轮询间隔 | `setup_timer()` 内 `self.feishu_timer.start` | 1800000ms（30 分钟） |
| 飞书 base token | 顶部 `FEISHU_BASE_TOKEN` | DcJzbLadCaGbGws2ZekchGHhnVe |
| 飞书表 ID | 顶部 `FEISHU_TABLE_ID` | tbl9DT9qniE63BH7 |
| 飞书视图名 | 顶部 `FEISHU_VIEW_NAME` | 时长 |
| 电池轮询间隔 | `update_display()` 内 `_battery_tick` 计数器 | 每 15 秒 |
| 计时器状态机 | `self.timer_state` | idle → running → paused → auto-restart |

## 运行和验证
```bash
# 启动看门狗（推荐，崩溃自动重启）
pythonw watchdog.py

# 直接启动主程序（调试用）
pythonw rest_reminder.py

# 验证进程
tasklist | findstr "pythonw.exe"

# 杀掉进程
taskkill /F /IM pythonw.exe
```

## 改完代码后必须做的
1. 杀掉旧进程：`taskkill /F /IM pythonw.exe`
2. 启动看门狗：`start "" pythonw watchdog.py`
3. 验证新进程 PID 已出现

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可

## 文档
- README.md — 用户文档（功能、安装、FAQ）
- 使用说明_完整版.txt — 详细操作指南
- 修复说明.md — 历史修复记录
- 后台运行说明.md — 启动方式详解
