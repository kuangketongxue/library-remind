# 休息提醒 — 架构文档

## 系统架构

```
┌─────────────────────────────────────────────────┐
│                 rest_reminder.py                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐ │
│  │ 主窗口    │  │ 浮窗系统  │  │ 托盘系统      │ │
│  │ Rest     │  │ Countdown│  │ FloatingBall  │ │
│  │ Reminder │  │ Overlay  │  │ SystemTray    │ │
│  │ Widget│  │ EyeRest  │  │               │ │
│  └────┬─────┘  └────┬─────┘  └──────┬────────┘ │
│       │             │               │           │
│  ┌────▼─────────────▼───────────────▼────────┐  │
│  │              storage.py (JSONStore)        │  │
│  │  goal_store / quotes_store / daily_store   │  │
│  │  settings_store / streak_store / etc.      │  │
│  └────────────────────┬──────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼──────────────────────┐  │
│  │              持久化文件 (.json)            │  │
│  │  .daily_log.json / .app_state.json / etc.  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 状态机

```
idle ──[开始]──> running ──[60min结束]──> resting ──[5min结束]──> idle
                      │                                       ▲
                      ├──[暂停]──> paused ──[继续]───────────┘
```

## 定时器架构

| 定时器 | 间隔 | 用途 |
|--------|------|------|
| `self.timer` | 1000ms | 主循环：更新显示、电池检测、状态保存 |
| `countdown._internal_timer` | 1000ms | 倒计时浮窗每秒更新 |
| `_glow_timer` | 50ms | 呼吸灯动画（窗口显示时运行） |
| `_stats_tick` | 300s | 保存历史统计 |
| `_state_save_tick` | 30s | 保存运行状态 |

## 数据流

```
用户操作 → RestReminderWidget → LocalSync → JSONStore → .json 文件
                                              ↓
                                         StatsWindow
                                         TrendWindow
```

## 设计系统

### 颜色
| Token | 值 | 用途 |
|-------|-----|------|
| `BG_DARK` | `#0c0c10` | 主背景 |
| `FG` | `#e8e6e1` | 主文字 |
| `FG_DIM` | `#666` | 辅助文字 |
| `ACCENT` | `#d4af37` | 主强调色（金色） |
| `ACCENT2` | `#ff7a50` | 暂停/次要按钮 |
| `INFO` | `#6a9bcc` | 22:00 倒计时 |
| `SUCCESS` | `#78B450` | 完成/学习 |

### 字体
| 用途 | 字体栈 |
|------|--------|
| UI 按钮 | Georgia, Noto Serif SC, serif |
| 数字/计时器 | Consolas, SF Mono, monospace |

### 圆角
- 窗口：16px
- 按钮：10px
- 倒计时浮层：16px

## 关键依赖

| 依赖 | 用途 |
|------|------|
| PyQt5 | GUI 框架 |
| psutil | 电池检测 |
| requests | B站 API / Supabase |
| ctypes | Win32 API（空闲检测、DPI、图标） |
| winreg | 开机自启 |
