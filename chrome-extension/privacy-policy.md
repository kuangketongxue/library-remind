# 隐私政策 — 精力管理 Chrome 扩展

> **Chrome Web Store 上架专用 | 托管地址：`https://crazy-rest-reminder.pages.dev/privacy-chrome`**

---

**生效日期：2026 年 7 月 13 日**

**开发者：kuangketongxue**

**联系方式：kuangketongxue@gmail.com**

**源码仓库：[github.com/kuangketongxue/library-remind](https://github.com/kuangketongxue/library-remind)**

---

## 1. 概述

「精力管理」Chrome 扩展（以下简称"本扩展"）是一款帮助用户管理学习节奏、定时休息、护眼的工具。本隐私政策说明本扩展收集、使用、共享哪些数据。本扩展遵循**数据最小化**原则，尽可能在本地完成所有功能。

## 2. 本地存储（不经过服务器）

本扩展通过 Chrome 的 `chrome.storage.local` API 在浏览器本地存储以下数据：

| 数据 | 用途 |
|---|---|
| 学习状态（计时器状态、轮次、学习/休息时长） | 驱动计时器显示和状态恢复 |
| 复盘记录（每轮评分、学科、标签、时间） | 生成趋势统计和成就系统 |
| 用户设置（学习/休息时长、护眼间隔、主题、通知开关） | 个性化体验 |
| 成就解锁记录 | 展示成就进度 |
| 连续打卡天数 | 展示连续打卡火焰 |

**这些数据全部存储在你的浏览器本地，不会自动上传到任何服务器。** 清除扩展或点击"设置 → 清除全部"即可彻底删除。

## 3. 可选的数据共享功能

以下功能仅在用户**主动配置并触发**时才会共享数据，每一项都是可选的：

### 3.1 GitHub 备份（可选）
- **触发条件**：用户在设置页填写 GitHub Token 和仓库名，点击"立即备份"或"恢复数据"
- **共享内容**：复盘记录、设置等本地数据
- **共享对象**：用户指定的 GitHub 仓库（通过 `https://api.github.com`）
- **注意**：GitHub Token 仅存储在浏览器本地，不会被发送到 GitHub 以外的任何服务器

### 3.2 邮件周报（可选）
- **触发条件**：用户在设置页填写收件人邮箱并启用"每周邮件"
- **共享内容**：学习统计摘要、邮件地址
- **共享对象**：通过 Cloudflare Worker 代理（`https://crazy-rest-reminder.pages.dev/api/send-email`）发送邮件

### 3.3 AI 学习报告（可选）
- **触发条件**：用户在"AI 报告"页面点击"生成"
- **共享内容**：近 7 天学习统计（轮次、评分）
- **共享对象**：通过 Cloudflare Worker 代理（`https://crazy-rest-reminder.pages.dev/api/ai-proxy`）调用 AI 模型生成报告
- **注意**：AI 报告生成后仅展示在浏览器内，不会被存储或共享给第三方

### 3.4 B 站链接（可选）
- **触发条件**：用户配置收藏夹/护眼视频 URL，且启用通知后轮次结束
- **共享内容**：无数据传输，仅在浏览器新标签页打开用户配置的 URL
- **行为等同于手动在浏览器地址栏输入网址**

## 4. 本扩展不收集的信息

**不会以任何方式收集：**
- 姓名、电话号码等个人身份信息
- 浏览历史或网页内容
- 位置信息
- Cookie 或网站登录凭证
- 未明确告知用户的任何数据

**没有**账号体系、没有跟踪脚本、没有遥测、没有广告。

## 5. 开源与审计

本扩展的开发者版本（Desktop 端）以 MIT 协议开源，托管在 GitHub：[github.com/kuangketongxue/library-remind](https://github.com/kuangketongxue/library-remind)。任何人都可以审查代码验证隐私声明的真实性。

Chrome 扩展代码包含在开源仓库的 `chrome-extension/` 目录中，同样可审计。

## 6. 数据存储与安全

- 本地数据通过 Chrome 的 `chrome.storage.local` API 存储，受浏览器沙箱保护，其他扩展和网页无法访问
- 可选的外部通信（GitHub API、Cloudflare Worker）全部通过 HTTPS 加密传输
- 开发者无法访问你本地存储的数据，也无法访问你 GitHub 仓库中的备份数据

## 7. 数据删除

你可以随时删除本扩展收集的数据：
- **删除今日数据**：设置页 → "重置今日"
- **删除全部数据**：设置页 → "清除全部"（不可恢复）
- **删除 GitHub 备份**：登录 GitHub 仓库手动删除 `chrome-ext-data/` 目录
- **删除扩展**：`chrome://extensions` → 移除扩展，本地数据随之清除

## 8. 未成年人保护

本扩展面向学习人群（包括未成年人），不主动收集个人身份信息。如果监护人认为未成年人在未经同意的情况下使用了可选共享功能，请通过下方联系方式要求删除相关数据。

## 9. 隐私政策变更

本隐私政策可能不时更新。更新后的版本将在本页发布并更新"生效日期"。重大变更将通过扩展更新通知用户。

## 10. 联系方式

如有隐私相关问题，请联系：
- **邮箱**：[kuangketongxue@gmail.com](mailto:kuangketongxue@gmail.com)
- **GitHub Issues**：[github.com/kuangketongxue/library-remind/issues](https://github.com/kuangketongxue/library-remind/issues)

---

> 本文件托管于 [crazy-rest-reminder.pages.dev](https://crazy-rest-reminder.pages.dev)，Chrome Web Store 上架时在开发者后台填入该地址。
