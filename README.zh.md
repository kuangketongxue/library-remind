<div align="center">

# 🖥️ 休息提醒

**智能桌面久坐提醒 · 学习工作两不误 · 开源免费**

[![Python](https://img.shields.io/badge/python-3.14%2B-yellow?style=for-the-badge)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey?style=for-the-badge)]()
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

[📥 免费下载](https://github.com/kuangketongxue/library-remind/releases/latest) · [🌐 官网](https://crazy-rest-reminder.pages.dev/) · [💬 反馈](https://github.com/kuangketongxue/library-remind/issues)

<a href="https://starcharts.cc/kuangketongxue/library-remind">
  <img src="https://starcharts.cc/kuangketongxue/library-remind/star-history.svg?bg=0c0c10&hideIssues=true" alt="Star History" height="180">
</a>

</div>

---

一款 Windows 桌面挂件，在长时间学习时提醒你起身休息。60 分钟专注循环、AI 学习分析、深色极简 UI。

**推荐使用**：双击 `_launch.vbs` 或运行 `python rest_reminder.py`。

## ✨ 功能一览

| 功能 | 说明 |
|------|------|
| **60分钟专注循环** | 学习 → 5分钟请辨倒计时 → 5分钟休息 → 自动开B站 |
| **5标签页主界面** | 今日概览 / AI报告 / 趋势分析 / 设置 / 关于 |
| **复盘记录** | 每小时学科 + 标签 + 评分 1-100 |
| **🤖 AI 学习分析** | 日报 / 周报 / 月报 / 季报 / 年报 |
| **趋势图表** | 学习时长柱状图 + 悬浮提示 |
| **20-20-20 护眼提醒** | 每20分钟轻量浮窗 |
| **托盘 + 浮球** | 后台常驻，一键控制 |
| **开机自启** | 系统登录后自动运行 |

## 🚀 快速开始

```bash
# 直接运行
python rest_reminder.py

# 或双击启动
_launch.vbs
```

## 📁 项目结构

```
├── rest_reminder.py        # 主程序（3836行）
├── storage.py              # 统一 JSON 存储层
├── tray_card.py            # 托盘卡片组件
├── vendor/                 # 本地依赖包
├── RestReminder.spec       # PyInstaller 配置
├── docs/ARCHITECTURE.md    # 架构文档
├── rest-reminder-site/     # 官网（Next.js）
```

## 🔗 相关链接

- [官网](https://crazy-rest-reminder.pages.dev/)
- [下载](https://github.com/kuangketongxue/library-remind/releases/latest)
- [更新日志](https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md)
- [架构文档](https://github.com/kuangketongxue/library-remind/blob/main/docs/ARCHITECTURE.md)

## 📄 开源协议

MIT License — 自由使用、修改、分发。

---

<div align="center">

**觉得有用？点个 ⭐ Star 支持一下！**

[English](README.md) · [日本語](README.ja.md)

</div>
