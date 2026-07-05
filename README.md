<div align="center">

# 🖥️ Rest Reminder

**Smart desktop break reminder — stay focused, stay healthy**

<a href="https://github.com/kuangketongxue/library-remind/actions">
  <img src="https://img.shields.io/github/actions/workflow/status/kuangketongxue/library-remind/ci.yml?style=for-the-badge" alt="CI">
</a>
<a href="https://github.com/kuangketongxue/library-remind/releases/latest">
  <img src="https://img.shields.io/github/v/release/kuangketongxue/library-remind?style=for-the-badge" alt="Release">
</a>
<a href="https://github.com/kuangketongxue/library-remind/stargazers">
  <img src="https://img.shields.io/github/stars/kuangketongxue/library-remind?style=for-the-badge&color=yellow" alt="Stars">
</a>
<a href="https://github.com/kuangketongxue/library-remind/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</a>
<a href="https://www.python.org/downloads/">
  <img src="https://img.shields.io/badge/python-3.14%2B-yellow?style=for-the-badge" alt="Python">
</a>
<a href="#">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey?style=for-the-badge" alt="Platform">
</a>

[📥 Download](https://github.com/kuangketongxue/library-remind/releases/latest) · [🌐 Website](https://crazy-rest-reminder.pages.dev/) · [📧 Contact](https://crazy-rest-reminder.pages.dev/contact) · [💬 Issues](https://github.com/kuangketongxue/library-remind/issues) · [中文](README.zh.md) · [日本語](README.ja.md)

<a href="https://starcharts.cc/kuangketongxue/library-remind">
  <img src="https://starcharts.cc/kuangketongxue/library-remind/star-history.svg?bg=0c0c10&hideIssues=true" alt="Star History" height="180">
</a>

</div>

---

A Windows desktop widget that reminds you to take breaks during long study sessions. 60-minute focus cycles, AI-powered learning analysis, and a calm dark UI that stays out of your way.

**Preferred setup**: double-click `_launch.bat` or run `python rest_reminder.py`.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **60-min Focus Cycle** | Study → 5-min mindfulness countdown → 5-min break → auto-open Bilibili |
| **5-Tab Dashboard** | Today / AI Report / Trends / Settings / About |
| **Review Logging** | Subject + tags + score (1-100) after each session |
| **🤖 AI Analysis** | Daily / weekly / monthly / quarterly / yearly reports. Auto-fallback to local wisdom quotes when network timeout — never blocks the UI |
| **Feishu Calendar** | Sync schedule to popup (via npm lark-cli) |
| **Trend Charts** | Study hours bar chart + time-of-day score heatmap |
| **20-20-20 Eye Care** | Gentle overlay every 20 minutes |
| **Tray + Floating Ball** | Background resident, one-click control |
| **Auto-start** | Launch on system login |
| **Achievements + Streaks** | 17 badges to keep you motivated |
| **Email Reports** | Scheduled weekly / monthly digests to your inbox |
| **GitHub Backup** | One-click backup + restore to a private repo |

## 🚀 Quick Start

```bash
# Run directly
python rest_reminder.py

# Or double-click
_launch.bat
```

## 📁 Project Structure

```
├── rest_reminder.py        # Main app (~4750 lines)
├── storage.py              # Unified JSON storage layer
├── tray_card.py            # Floating tray card widget
├── feishu_calendar.py      # Feishu / Lark calendar integration
├── backup.py               # GitHub backup / restore
├── vendor/                 # Bundled dependencies
├── RestReminder.spec       # PyInstaller config
├── docs/ARCHITECTURE.md    # Architecture docs
├── rest-reminder-site/     # Website (Next.js) — includes pricing / privacy / rules / terms
└── README.zh.md            # 中文版
└── README.ja.md            # 日本語版
```

## 🔗 Links

- [Website](https://crazy-rest-reminder.pages.dev/) — Official site
- [Releases](https://github.com/kuangketongxue/library-remind/releases) — Download latest
- [Changelog](https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md) — Version history
- [Architecture](https://github.com/kuangketongxue/library-remind/blob/main/docs/ARCHITECTURE.md) — System design

## 📄 License

MIT — free to use, modify, distribute.

---

<div align="center">

**If you find it useful, give it a ⭐ Star!**



</div>
