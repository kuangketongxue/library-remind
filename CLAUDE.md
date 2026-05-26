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
| 飞书 base token | 顶部 `FEISHU_BASE_TOKEN` | DcJzbLadCaGbGws2ZekchGHhnVe |
| 飞书表 ID | 顶部 `FEISHU_TABLE_ID` | tbl9DT9qniE63BH7 |
| 计时器状态机 | `self.timer_state` | idle → running → paused → auto-restart |

## 运行和验证
```bash
# 启动看门狗（推荐，崩溃自动重启）
pythonw watchdog.py

# 直接启动主程序（调试用）
pythonw rest_reminder.py

# 杀掉所有进程
taskkill /F /IM pythonw.exe

# 用 PowerShell 验证并重启
Get-Process pythonw | Stop-Process -Force
Start-Process -WindowStyle Hidden -FilePath "C:\Users\binlo\AppData\Local\Python\bin\pythonw.exe" -ArgumentList "C:\Users\binlo\Desktop\休息提醒\rest_reminder.py" -WorkingDirectory "C:\Users\binlo\Desktop\休息提醒" -PassThru
```

## 踩坑记录（必读）
- **lark-cli 是 .cmd 管道脚本**：`subprocess.run()` 在 Windows 上必须 `shell=True` 才能执行 `.cmd`，否则返回码 1 + 空 stdout。`_call_lark` 已加 `shell=(sys.platform == 'win32')`
- **`+record-list` 分页**：该表超过 200 条记录，`_find_today_record()` 必须用 `--offset` 逐页遍历到 `has_more: false`，否则翻页后的记录找不到会被误判为"不存在"而重复创建
- **lark-cli JSON 编码**：Windows 下 `+record-list --format json` 返回的 `fields` 中文字段名编码可能损坏，必须用 `field_id_list`（如 `fldTXDs0Ro`）定位列索引
- **`+record-upsert` 返回结构**：`data.record.record_id_list[0]` 取新记录 ID，`data.record.fields` / `data.record.field_id_list` 映射列名

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——改 README changelog 即可

## 文档
- README.md — 用户文档（功能、安装、FAQ）
- 版本记录.md — 更新日志
