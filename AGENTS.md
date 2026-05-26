# 休息提醒 — AGENTS.md

## 项目概述
PyQt5 桌面挂件：60 分钟计时（自动循环）+ 暂停/继续 + 每小时随机打开 B 站收藏夹视频 + 每 3 小时打开护眼视频 + 电池监控 +22:00 倒计时。绿色小浮球：点击显示/隐藏主窗口，可拖动。看门狗守护：watchdog.py 监控主进程，崩溃自动重启，开机自启动指向看门狗。

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
| 电脑使用缓存 | `.computer_usage.json` | 自动创建，跨重启持久化 |
| 倒计时浮层坐标 | `.overlay_pos.json` | 拖动后自动保存，跨重启记忆 |
| 倒计时浮层尺寸 | `CountdownOverlay.setFixedSize` | 200×110px |
| 倒计时触发阈值 | `_handle_running` / `update_computer_usage` | 最后 300 秒（5 分钟） |
| 倒计时浮层拖拽 | `CountdownOverlay.eventFilter` | 子组件事件过滤器转发鼠标事件 |
| 窗口尺寸 | `init_ui()` 内 `widget_width/widget_height` | 340×380 |
| 倒计时范围 | `update_display()` 内 `start_minutes/end_minutes` | 4:30~22:00（倒计时模式） |
| 学习目标时长 | `study_progress_bar.setMaximum` | 14（14 小时） |
| 电池轮询间隔 | `update_display()` 内 `_battery_tick` 计数器 | 每 15 秒 |
| 飞书同步（实时） | `FeishuSync` (L:115) | 学习每 +1h → 飞书 / 电脑每 +3h → 飞书 |
| 飞书 base token | 环境变量 `FEISHU_BASE_TOKEN` | 必填（开源版不包含默认值） |
| 飞书表 ID | 环境变量 `FEISHU_TABLE_ID` | 必填（开源版不包含默认值） |
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
- 版本记录.md — 更新日志