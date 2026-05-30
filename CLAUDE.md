# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：60 分钟计时（自动循环）+ 暂停/继续 + 每小时随机打开 B 站收藏夹视频 + 每 3 小时打开护眼视频 + 电池监控 +22:00 倒计时 + 数据本地持久化。绿色小浮球：点击显示/隐藏主窗口，可拖动。看门狗守护：watchdog.py 监控主进程，崩溃自动重启，开机自启动指向看门狗。

## 技术栈
Python 3.7+ / PyQt5 / requests / psutil

## 关键文件
```
rest_reminder.py        — 主程序（所有逻辑都在这一个文件）
watchdog.py             — 看门狗进程（监控主进程，崩溃自动重启，CREATE_NO_WINDOW 静默）
cute_icon.png / .ico    — 托盘和任务栏图标
requirements.txt        — 依赖：PyQt5, requests, psutil
一键安装.bat             — 安装 + 自启动 + 启动看门狗（推荐用户入口）
完全独立启动.vbs          — 独立 VBS 启动脚本（硬编码 pythonw 绝对路径，桌面双击用）
```

## 关键配置位置
| 配置 | 位置 | 默认值 |
|---|---|---|
| 提醒间隔 | `self.interval_minutes` | 60 分钟（自动循环） |
| 收藏夹 ID | `get_bilibili_videos()` 内 `fid` | 3648313921 |
| 用户 ID | `get_bilibili_videos()` 内 `mid` | 529362421 |
| 护眼视频 URL | `show_computer_usage_reminder()` | BV14Y4y1N7PW |
| 电脑使用周期 | `update_computer_usage()` | 每 3 小时循环提醒 |
| 电脑使用缓存 | `.computer_usage.json` | 自动创建，跨重启持久化 |
| 倒计时浮层坐标 | `.overlay_pos.json` | 拖动后自动保存，跨重启记忆 |
| 学习目标时长 | `study_progress_bar.setMaximum` | 14（14 小时） |
| 每日数据存储 | `.daily_log.json` | 学习+电脑时长，跨重启持久化 |
| 计时器状态机 | `self.timer_state` | idle → running → paused → auto-restart |

## 运行和验证
```bash
# 启动看门狗（推荐，崩溃自动重启）
# 必须用真实 Python 路径，避免 WindowsApps 代理导致双实例
pythonw watchdog.py
# 或指定真实路径：
# C:\Users\<user>\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe watchdog.py

# 直接启动主程序（调试用）
pythonw rest_reminder.py

# 杀掉所有进程
taskkill /F /IM pythonw.exe

# PowerShell 验证并重启
Get-Process pythonw | Stop-Process -Force
$real_pythonw = "C:\Users\<user>\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
Start-Process -WindowStyle Hidden -FilePath $real_pythonw -ArgumentList "watchdog.py" -WorkingDirectory "path\to\休息提醒"
```

## 踩坑记录（必读）
- **SingleInstanceChecker 必须模块级生命周期**：如果放在 `main()` 作为局部变量，GC 回收后 `__del__` 删除锁文件→watchdog 误判主进程已死→反复重启。已修复为 `_single_instance = SingleInstanceChecker()` 模块级变量
- **WindowsApps pythonw.exe 是 Store 代理**：文件 < 100KB，fork 时会额外启动一个 watchdog 进程导致双实例。watchdog.py 和 rest_reminder.py 已加代理检测，自动从 PATH 找真实 Python
- **注册表自启动必须指向 watchdog.py**：指向 rest_reminder.py 则崩溃后无守护，无法自动恢复

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可

## 文档
- README.md — 用户文档（功能、安装、FAQ）
- 版本记录.md — 更新日志
