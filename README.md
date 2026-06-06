<div align="center">

# 🖥️ Rest Reminder

**智能桌面久坐提醒 · 学习工作两不误**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%2010/11-lightgrey.svg)]()
[![Stars](https://img.shields.io/github/stars/kuangketongxue/library-remind?style=social)]()

[📥 免费下载](https://github.com/kuangketongxue/library-remind/releases/latest) · [🌐 官网](https://rest-reminder-app.netlify.app) · [💬 反馈](https://github.com/kuangketongxue/library-remind/issues)

</div>

---

## 📸 截图

<div align="center">

| 主界面 | 学习统计 | 系统托盘 |
|:---:|:---:|:---:|
| ![主界面](public/screenshot-main.png) | ![统计](public/screenshot-stats.png) | ![菜单](public/screenshot-menu.png) |

</div>

## ✨ 功能一览

| 功能 | 🆓 免费版 | 💎 Pro版 |
|------|:---------:|:--------:|
| 60分钟循环休息提醒 | ✅ | ✅ |
| 自定义提醒间隔（15-120分钟） | ❌ | ✅ |
| B站护眼/放松视频自动播放 | ✅ | ✅ |
| 用户自定义收藏夹和视频 | ✅ | ✅ |
| 学习时长追踪 | ✅ | ✅ |
| 连续打卡统计 | ✅ | ✅ |
| 电脑使用时长监控（每3小时提醒） | ✅ | ✅ |
| 云同步（数据永不丢失） | ❌ | ✅ |
| 周报/月报统计 | ❌ | ✅ |
| 数据导出（CSV） | ❌ | ✅ |
| 多主题（护眼绿/极简白/深海蓝） | ❌ | ✅ |
| 开机自启 + 崩溃自动重启 | ✅ | ✅ |

**Pro版：19.9元/月** · [升级方式见官网](https://rest-reminder-app.netlify.app)

## 🎁 推荐返利

分享推荐码给朋友，**双方各得7天免费Pro！**

## 🚀 快速开始

### 方式一：下载 exe（推荐）

1. [下载最新版](https://github.com/kuangketongxue/library-remind/releases/latest) `RestReminder.exe`
2. 双击运行
3. 系统托盘找到绿色小球，右键设置

### 方式二：源码运行

```bash
# 克隆仓库
git clone https://github.com/kuangketongxue/library-remind.git
cd library-remind

# 安装依赖
pip install -r requirements.txt

# 启动（推荐通过看门狗，崩溃自动重启）
pythonw watchdog.py
```

## 🔧 自定义设置

右键托盘图标 → ⚙️ 设置：

- **B站收藏夹**：填入你的收藏夹 ID，休息时打开你的视频
- **提醒视频**：填入 BV 号，自定义休息时播放的视频
- **提醒间隔**：Pro版可自定义 15-120 分钟

## 📁 项目结构

```
├── rest_reminder.py        # 主程序（所有逻辑）
├── watchdog.py             # 看门狗（崩溃自动重启）
├── cute_icon.png/ico       # 图标
├── requirements.txt        # 依赖
├── 一键安装.bat             # 安装+自启动
├── 完全独立启动.vbs          # 独立启动脚本
└── dist/RestReminder.exe   # 打包好的 exe
```

## 🔒 隐私声明

- **免费版**：所有数据存储在本地，不联网，不上传任何信息
- **Pro版**：云同步数据加密存储于 [Supabase](https://supabase.com)，仅你本人可访问
- **我们不收集、不共享、不出售任何用户数据**

## 🐛 问题反馈

遇到问题？请到 [Issues](https://github.com/kuangketongxue/library-remind/issues) 提交，附上：

1. 操作系统版本
2. Python 版本（如源码运行）
3. `rest_reminder.log` 日志文件（程序目录下）

## 📄 更新日志

查看 [CHANGELOG.md](CHANGELOG.md)

## 📄 License

[MIT License](LICENSE) — 自由使用、修改、分发

---

<div align="center">

**如果觉得有用，点个 ⭐ Star 支持一下！**

</div>
