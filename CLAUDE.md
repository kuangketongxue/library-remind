# 休息提醒 — CLAUDE.md

## 项目概述
PyQt5 桌面挂件：60 分钟计时（自动循环）+ 暂停/继续 + 每小时随机打开 B 站收藏夹视频 + 每 3 小时打开护眼视频 + 电池监控 +22:00 倒计时 + 飞书实时同步。绿色小浮球：点击显示/隐藏主窗口，可拖动。看门狗守护：watchdog.py 监控主进程，崩溃自动重启，开机自启动指向看门狗。

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
| 飞书凭据 | 环境变量 `FEISHU_BASE_TOKEN` / `FEISHU_TABLE_ID`，或 `config.json` 兜底 | 必填 |
| 飞书表 ID | 环境变量 `FEISHU_TABLE_ID`，或 `config.json` 兜底 | 必填 |
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

## 环境变量（飞书同步必需）
飞书同步功能要求以下变量设为 Windows **用户级**环境变量（`setx` 写注册表，只对新进程生效）：
```bat
setx FEISHU_BASE_TOKEN "DcJzbLadCaGbGws2ZekchGHhnVe"
setx FEISHU_TABLE_ID "tbl9DT9qniE63BH7"
```
设完后必须**重启 watchdog + rest_reminder 进程链**，已在运行的进程不会自动获取新变量。

**config.json 兜底**：如果环境变量不可用（如 pythonw 子进程继承失败），代码会从项目目录的 `config.json` 读取：
```json
{
  "FEISHU_BASE_TOKEN": "DcJzbLadCaGbGws2ZekchGHhnVe",
  "FEISHU_TABLE_ID": "tbl9DT9qniE63BH7"
}
```

## 踩坑记录（必读）
- **lark-cli 是 .cmd 管道脚本**：`subprocess.run()` 在 Windows 上必须 `shell=True` 才能执行 `.cmd`，否则返回码 1 + 空 stdout。但如果 .cmd 包装器损坏或 pythonw 上下文不兼容，返回码 255 + GBK 乱码。**已修复**：`_call_lark` 先用 shell=True，失败后 fallback 到 Node.js 直接调 `scripts/run.js`
- **`+record-list` 分页**：该表超过 200 条记录，`_find_today_record()` 必须用 `--offset` 逐页遍历到 `has_more: false`，否则翻页后的记录找不到会被误判为"不存在"而重复创建
- **lark-cli JSON 编码**：Windows 下 `+record-list --format json` 返回的 `fields` 中文字段名编码可能损坏，必须用 `field_id_list`（如 `fldTXDs0Ro`）定位列索引
- **`+record-upsert` 返回结构**：`data.record.record_id_list[0]` 取新记录 ID，`data.record.fields` / `data.record.field_id_list` 映射列列名
- **@file 路径校验失败**：lark-cli 1.0.39+ 偶发将相对路径转绝对路径后拒绝。**已修复**：始终用内联 JSON（不用 @file）
- **SingleInstanceChecker 必须模块级生命周期**：如果放在 `main()` 作为局部变量，GC 回收后 `__del__` 删除锁文件→watchdog 误判主进程已死→反复重启。已修复为 `_single_instance = SingleInstanceChecker()` 模块级变量
- **WindowsApps pythonw.exe 是 Store 代理**：文件 < 100KB，fork 时会额外启动一个 watchdog 进程导致双实例。watchdog.py 和 rest_reminder.py 已加代理检测，自动从 PATH 找真实 Python
- **注册表自启动必须指向 watchdog.py**：指向 rest_reminder.py 则崩溃后无守护，无法自动恢复
- **`setx` 环境变量对已运行进程不生效**：设完必须重启整个进程链。**已修复**：代码现在从 `config.json` 兜底读取飞书凭据

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可

## 文档
- README.md — 用户文档（功能、安装、FAQ）
- 版本记录.md — 更新日志
