# 更新日志

所有重要版本更新记录。

## 全面扫描修复 v6.2.12 (2026-07-17) — 桌面版 3 崩溃修复 + 扩展安全加固 + 官网全面修复

### 🐛 桌面版崩溃修复（P0）
- **TrendWindow `_score_to_color` NameError 崩溃**：函数体被错误嵌入 `_is_newer` 的 return 之后（死代码），导致所有趋势页面渲染时 NameError。提取为独立函数
- **`insertWidget(idx, None)` 崩溃**：`_build_ai_tab()` 在已构建时返回 None，`insertWidget` 接收 None 抛 TypeError。加 None 守卫
- **`_decrypt_key` 返回密文作为 API key**：解密失败时返回 `enc:...` 密文字符串，被当作 API key 发往服务器导致 401。改为返回 None，调用方优雅降级

### 🔒 Chrome 扩展安全 + 功能修复
- **移除 `<all_urls>` host 权限**：`chrome.scripting.insertCSS` 不需要该权限，移除后通过 CWS 审核更容易
- **成就统计改为累计数据**：`getAchievementStats` 从只用今日数据改为跨天累计（新增 `totalStudyAllTime` 字段持久化），成就系统终于能正常解锁
- **休息/复盘时长读取用户设置**：`rest.html` 和 `review.html` 从 storage 读取 `restMinutes` / `focusMinutes`，不再硬编码

### 🌐 官网全面修复
- **面包屑链接文字修复**：5 个子页面（docs/pricing/terms/rules/privacy）面包屑首页链接显示"文档"→改为"Rest Reminder"
- **Sponsor 动画修复**：从 mount 即播放改为 `whileInView`（滚动到才触发），避免用户看不到动画
- **Sponsor 网格修复**：`grid-cols-5` → `grid-cols-3`（3 个技术伙伴不需要 5 列）
- **Navbar 图标修复**：从 `app-icon.png`（2172×724 横幅图）改为 `favicon.png`（256×256 正方形）
- **CSS 重复 keyframes 清理**：`fade-in-up` + `fadeInUp` 合并为单一 `fadeInUp`
- **i18n 补全**：7 个缺失翻译 key（`hero.banner.alt`/`hero.video.alt`/`nav.language_switch`/`site.title`/`site.description`/`notice.col_category`/`notice.col_official`），三语同步
- **版本号统一**：`download.note` 从 v6.2.0 更新为 v6.2.10
- **死文件清理**：删除 `app-icon.png`（1225KB 横幅）、`hero-banner.png`（278KB 未引用）、`hero-rest-banner.jpg`、`screenshot-menu.png`
- **Footer CTA 按钮**：从手写样式改为 `btn-primary`，hover 行为与全局一致
- **DocsNav**：移除未使用的 `Link` import

### 📦 安装
```
git pull && C:\Python314\python.exe rest_reminder.py
```

---

## 官网 UI 全面修复 + 认证徽章 v6.2.11 (2026-07-17) — 10 项修复 + Fable 5 / GPT Sol 认证

### 🎨 官网 UI 修复（10 项）
- **Navbar 三图改一图**：移除 favicon.ico 和 hero-rest-banner.jpg，仅保留 app-icon.png + 品牌文字
- **Hero 版本号修正**：v6.2.6 → v6.2.10
- **Changelog 页版本号修正**：从 Chrome 扩展版（v1.x）改为桌面版（v6.2.10/v6.2.9/v6.2.8/v6.2.7/v6.2.6）
- **Footer 更新日志链接修正**：从 GitHub CHANGELOG.md → 站内 /changelog
- **移动端导航菜单**：新增 hamburger 按钮 + 下拉菜单（导航/语言/主题/GitHub/下载）
- **CSS @import 顺序修复**：Google Fonts 移到 Tailwind 之前，消除构建警告
- **删除空 body::before**：opacity:0 无实际作用的伪元素
- **删除未使用的 breathe 动画**：CSS 定义但从未引用
- **不必要的图片 preload 清理**：hero-rest-banner.jpg 等不再被 Navbar 引用后自动消除
- **Docs 页重复 changelog 替换为链接卡片**：避免与独立 /changelog 页内容重复

### 🏅 认证徽章
- **新增 Fable 5 Verified + GPT Sol Verified 认证徽章**
- 官网 Hero 区（统计数字下方）、桌面版关于页（品牌 Hero 区）、Chrome 扩展 popup（底部链接下方）
- PyInstaller spec 同步更新，打包时自动包含徽章图片

### 📦 安装
```
git pull && C:\Python314\python.exe rest_reminder.py
```

---

## 开机自启修复 v6.2.10 (2026-07-15) — 双启动修复 + 单实例锁修复 + 安装/卸载脚本统一

### 🐛 关键修复：开机启动 2 个实例
- **根因**：存在两套独立的自启机制（注册表 Run 键 + 启动文件夹 `.lnk`），且 Windows Named Mutex 用 `bInitialOwner=False`（创建者不持有），第二个进程永远检测不到"被持有" → 两套机制同时触发就启动 2 个实例
- **单实例锁修复**：`CreateMutexW(None, True, ...)` 让创建者立即持有 mutex，第二个进程 `WaitForSingleObject(0)` 正确返回 WAIT_TIMEOUT 后退出
- **验证**：本地对抗性测试（几乎同时启动 2 个进程）→ A=`FIRST_OWNER`、B=`SECOND_BLOCKED` PASS；系统启动残留全清理，PS 实测残留 0 / 进程 0

### 🔧 自启机制统一
- `set_autostart()` 无论启用/禁用都同步清理 `.lnk`，**统一为注册表单一启动源**，避免两套机制并存
- `is_autostart_enabled()` 注册表 Run 键和 `.lnk` 任一存在即视为"已开启"，修复 UI 显示"已关闭"但实际仍能自启
- 新增 `_get_startup_lnk_path` / `_remove_startup_lnk` 两个 helper，职责单一

### 🔧 安装/卸载脚本修复
- `一键安装.bat`：创建 `.lnk` → 改为写注册表（与 `set_autostart(True)` 一致），安装时顺手清理残留旧 `.lnk`
- `卸载.bat`：只删 `.lnk` → 改为三处都删（注册表 Run 键 + StartupApproved + `.lnk`），卸载不再残留自启

### 📦 安装
```
git pull && C:\Python314\python.exe rest_reminder.py
```

---

## 隐私修复 v6.2.9 (2026-07-15) — 隐私保护 + 时间价值体系常驻化 + 官网国际化

### 🔒 隐私保护（重要）
- **移除源码中硬编码的个人标识**：bilibili UID（`529362421`）和收藏夹 ID（`3648313921`）从开源代码中彻底移除，改为从本地加密 `.settings.json` 的 `bilibili_mid` / `bilibili_fid` 读取——推开源仓库不再泄露个人账号
- **通用化 URL**：B 站收藏夹链接改为模板 `https://space.bilibili.com/{mid}/favlist?fid={fid}`，mid/fid 从本地注入；护眼视频 URL 不含个人数据可保留硬编码
- **tray_card / rest_reminder.py** 中 B 站/收藏夹引用全部模板化

### 🆕 时间价值体系（常驻功能）
- **复盘窗口新增"时间价值"输入区**：可选输入「理想分薪（元/min）」+「状态加权（0.5~1.5）」，实时显示 ¥/min 和 ¥/时
- **自动计算并持久化**：每次复盘自动写入 `per_min / round_value / cum_debt / eff_per_min`
- **公式**：每分钟价值=分薪×加权；每小时价值=×60；累计时间负债=历史累计+本轮；效率=累计负债÷累计轮数
- **今日 tab 卡片**：新增今日时间价值、累计时间负债、时间负债效率显示
- **记忆默认值**：上次输入作为下次默认值

### 🔧 常驻版本更新检查
- 启动 5 分钟后首次自动检查，之后每小时一次；发现新版本弹窗"前往更新"或"跳过此版本"
- 去重：用户点击"跳过"后该版本在设置里标记，不再重复弹窗
- 健壮版本解析：正确比较 `v6.2.10 > v6.2.9`、`6.2.9.1 > 6.2.9`、跳过 `-beta` 误报
- 失败回退优化：不再调用含个人 URL 的占位符

### 🌐 国际版官网 (zh/en/ja)
- **官网全面国际化 (zh/en/ja)**：`i18n` 词汇表 + 语言切换（localStorage 持久化）+ Navbar / Footer / Hero / WhyChoose / Features / Pricing / Testimonials / Sponsor / 文档 / 隐私 / 条款 / 规则 / 联系 全部三语
- 新增 `rest-reminder-site/src/lib/i18n.tsx`（2100+ 条）+ `changelog/page.tsx` 国际化
- 修复桌面版崩溃：`_prompt_goal` 改为异步调用，避免初始化时同步弹窗崩溃
- 修复 Navbar / Footer / Hero 硬编码颜色 + alt 缺失 + 响应式 + MetadataSync

### 🗂️ 官网维护
- 修复 i18n changelog block keys 尾逗号一致性

### 📦 安装
```
git pull && C:\Python314\python.exe rest_reminder.py
```

---

## 公告弹窗再版 v6.2.8 (2026-07-15) — 公告内容 + 防骗声明改版 + WebP 优化

### 📢 公告改版
- **公告弹窗再版**：内容从参考图对齐 → 编号项 + 子弹点格式（feat: `公告弹窗改版 — 编号项+子弹点格式，与参考图一致`）
- **公告恢复更新内容 + 防骗声明合并弹窗**：用户反馈公告弹窗长期未更新内容 → 恢复更新内容，并合并防骗声明到公告弹窗
- **防骗声明移到首页弹窗，移除每页横幅**：删除 `OfficialNotice.tsx`（55行横幅），统一到 AnnouncementModal 弹窗

### 🖼️ WebP 图片优化 — 首屏加载提速 94%
- **Hero 主图 / Hero 背景大图**：PNG → WebP，首屏加载提速 94%
- Hugo 风格命名：`hero-banner-promo.webp`、`hero-banner.webp`
- `Hero.tsx` / `page.tsx` 改用 WebP 资源

---

## 官网修复 v6.2.7 (2026-07-13) — 图标/视频/主题全面修复

### 🔧 问题修复
- **图标消失修复**：favicon 从 1.1MB 的 `logo-eye.png` 改为 37KB 的 `favicon.png`，浏览器无法解码超大的 favicon 文件；导航栏 logo 同步改用 `favicon.png`，页脚大图改用 `rest-reminder-logo.png`(145KB)
- **背景视频消失修复**：`<video>` 添加 `preload="auto"`，确保浏览器加载足够帧数以支持 autoplay；修复 `useEffect` 依赖数组无限循环 bug（`playing` state → `playingRef`，依赖数组改为 `[]`）
- **CSS @import 顺序修复**：Google Fonts `@import` 从 Tailwind `@import` 之后移到之前，消除浏览器 CSS 警告
- **主题闪烁修复**：在 `<html>` 标签加内联脚本，React 水合前就读取 localStorage + system preference 设置 `dark` class，消除浅色→深色闪烁
- **缺失 CSS 类补全**：添加 `section-glow`（区块顶部微光晕）和 `btn-shine`（按钮悬停光泽动画）定义，修复 WhyChoose/Testimonials/Pricing 区块样式缺失

---

## Chrome 扩展 v1.3.0 (2026-07-13) — 功能补齐 + 体验升级

### 🆕 新功能
- **休息倒计时弹窗**：rest.html 5 分钟弹窗，圆环进度条 + 横条进度 + 大字倒计时 + 智能提示语（"准备开始学习"/"请回到电脑前"）
- **声音提醒**：休息和复盘开始时播放和弦铃音（Web Audio API 本地生成），设置页可关
- **暂停超时提醒**：暂停超过 2 分钟弹桌面通知"继续还是结束本轮？"
- **自动开始下一轮**：复盘提交后 3 秒自动进入下一轮（可关，默认关）
- **灰阶滤镜**：专注期间所有标签页自动变灰（grayscale 100%），popup 一键开关
- **动态工具栏图标**：OffscreenCanvas 生成圆环进度 + 剩余分钟数，不同状态不同颜色
- **深度专注评分**：深度分 = 自评分 × 完成度 × 专注度 × 连续性，复盘页三因子实时展示

### 🔧 设置页修复
- **设置真正生效**：学习时长/休息时长/护眼间隔从写死常量改为读取 storage，修改后立即生效
- **新增设置项**：休息提示音开关、自动开始下一轮开关

### 🔒 合规
- **隐私政策上线**：crazy-rest-reminder.pages.dev/privacy-chrome，Chrome Web Store 上架专用
- **CWS 上架指南**：权限说明、商品详情文案、打包清单模板
- **manifest 清理**：删除 web_accessible_resources: \<all_urls\>、加 minimum_chrome_version: 88、options_page → options_ui

### 📦 安装
```
Chrome → chrome://extensions/ → 开发者模式 → 加载已解压 → 选 chrome-extension/ 目录
```

---

## Chrome 扩展 v1.2.0 (2026-07-10) — 完整功能版

### 🚀 核心功能
- **60+5 分钟学习循环**：60分钟计时 → 5分钟休息 → 自动弹复盘
- **复盘评分 1-100**：滑块评分 + 7学科选择(语数英物化政其他) + 5标签(专注/疲劳/收获大/走神/其他)
- **B 站联动**：每轮结束自动打开收藏夹，每3轮打开护眼视频
- **20-20-20 护眼**：每20分钟弹窗提醒看远处20秒，带进度环倒计时
- **Badge 倒计时**：扩展图标显示剩余分钟数
- **22:00 硬限制**：过时按钮变灰，不开始新轮次

### 🎯 数据与统计
- **连续打卡**：自动计算连续打卡天数
- **轮次目标提示**：开始前弹窗问"这轮学什么"
- **趋势分析**：近7天评分柱状图 + 今日复盘记录
- **成就系统**：16个徽章（学习/打卡/复盘/轮次），解锁通知
- **AI 学习报告**：日报/周报/月报/季报，调 Cloudflare 代理生成

### 🎨 体验
- **环境白噪音**：5种音效（雨声/森林/咖啡馆/白噪音/棕色噪音）
- **主题切换**：深色/浅色，CSS 变量全局适配
- **首次使用引导**：3页新手教程
- **数据导出**：一键下载 JSON 备份文件

### 💾 集成
- **GitHub 备份**：直接调 GitHub API 备份/恢复（设置页填 Token）
- **飞书日历**：通过 Cloudflare Worker 代理获取日程
- **邮件周报**：通过 Cloudflare Worker 代理发送
- **B 站链接可配置**：设置页填自己的收藏夹 URL

### 📦 安装
```
Chrome → chrome://extensions/ → 开发者模式 → 加载已解压 → 选 chrome-extension/ 目录
```

---

## 桌面版 v6.2.8–v6.2.9 (2026-07-10)

### 🐛 Bug 修复
- **程序无法退出**：`flush_pending_settings` 缺少 `@classmethod` 装饰器，TypeError 导致退出流程被吞
- **飞书日程获取失败**：`feishu_calendar.py` 缺少 `import sys`
- **周报线程泄漏**：`_check_weekly_report` 不清理旧 worker

### ⚡ 性能优化
- `setStyleSheet` 仅状态变化时调用（减少 Qt 样式重解析）
- 数据卡片每 5 秒更新，日程刷新每 30 秒
- `_save_active_state` 脏检查，状态不变时跳过磁盘写入

### 🎯 UX 改善
- 主界面新增「开始学习」大按钮
- 主窗口顶部拖动栏
- 复盘弹窗去掉 60 秒强制倒计时

### ♻️ 重构
- 删除电池充电保护功能

## v6.2.9 (2026-07-10) — 性能优化 + 核心体验改善

### ⚡ 性能优化
- **今日 tab 刷新降频**：数据卡片每 5 秒更新（原来每秒），日程刷新每 30 秒（原来每秒），Qt 样式仅状态变化时重建
- **状态保存脏检查**：`_save_active_state` 仅在状态/轮次/休息时长变化时写入磁盘，避免每 30 秒无意义的原子写入
- **计时器文本优化**：仅秒数整数变化时更新 QLabel，减少无意义的 setText 调用

### 🎯 UX 改善
- **主界面「开始学习」按钮**：今日 tab 顶部新增醒目的开始/暂停按钮，不再需要通过浮球 popup 启动学习
- **主窗口可拖动**：顶部 5px 隐藏拖动栏，FramelessWindowHint 窗口终于可以拖动了
- **复盘弹窗非阻塞**：去掉 60 秒强制倒计时自动提交，改为「方便时提交」，不再打断用户的休息流程

## v6.2.8 (2026-07-10) — 修复无法退出 + 飞书日程获取失败

### 🐛 Bug 修复
- **程序无法退出**：`LocalSync.flush_pending_settings` 缺少 `@classmethod` 装饰器，导致 `quit_app` 调用时抛 TypeError，退出流程被 except 吞掉，程序永远卡死
- **quit_app 双重保险**：`os._exit(0)` 移到 try/except 外层，即使 quit_app 内部异常也能强制退出
- **飞书日程获取失败**：`feishu_calendar.py` 缺少 `import sys`，lark-cli 启动时 `sys.platform` 抛 NameError，日程全部获取失败
- **周报线程泄漏**：`_check_weekly_report` 创建新 worker 前未清理旧 worker，可能导致线程堆叠

## v6.2.7 (2026-07-09) — 桌面按钮优化 + 官网多语言/主题 + 唯一官方渠道声明

### 🎨 桌面应用界面优化
- **关于页按钮加 emoji**：官网🌐、更新日志📋、检查更新🔄，提升识别度
- **GitHub 图标**：保持真实 SVG 渲染，确保图标清晰

### 🌐 官网全面升级
- **多语言支持**：新增 CN / EN / JP 三语言切换（localStorage 持久化）
- **日/夜模式**：新增主题切换按钮，暗色主题覆盖全局 CSS 变量
- **GitHub 真实图标**：Navbar / Footer 的 GitHub 链接从文字改为真实 cat SVG 图标
- **唯一官方渠道声明**：Navbar 下方常驻 OfficialNotice 横幅（Warning + 表格 + 反诈提醒）

### 🐛 Bug 修复
- **AI 服务不可用提示优化**：default_proxy 增加最多 3 次自动重试；连接失败时提示更友好，不再展示原始 urllib3 堆栈
- **今日 tab 记录显示 "-"**：`_Utils.md_to_html` bullet 检测统一用 `lstrip()`，修复带缩进 markdown 渲染异常
- **单实例 Mutex stale lock**：`ERROR_ALREADY_EXISTS` 后增加 `WaitForSingleObject(handle, 0)` 判断，崩溃后 mutex 不再拦新实例
- **官网 Hero 视频背景**：10MB 视频加载慢导致背景空白，改为 hero-banner.png 静态兜底 + 视频渐入
- **公告弹窗逻辑**：移除 localStorage 记忆，每次访问弹出；检测路径仅首页(/)触发
- **部署命令修正**：Cloudflare Pages 必须用 `wrangler pages deploy out` 部署构建产物

## v6.2.6 (2026-07-06) — 官网全面修复

### 🐛 Bug 修复
- **浏览器标签页图标**：favicon 换为 256x256 cute_icon.png（37KB），修复显示通用文档图标问题
- **Contact 页面内容不可见**：framer-motion `initial={{ opacity: 0 }}` 在 Next.js 静态导出时不执行动画。改用 CSS `@keyframes fadeInUp`
- **Contact 页面图标**：邮箱和微信图标从通用 SVG/emoji 改为官方品牌图标（Gmail 红色信封 M、WeChat 绿色对话气泡）
- **Hero 背景视频不播放**：视频 10MB 加载慢导致背景空白。改为 hero-banner.png 静态兜底 + 视频立即 autoPlay
- **公告弹窗文字看不清**：CSS 变量在暗背景上太暗。改为显式亮色（白色标题、#ccc 正文）

### 📢 新功能
- **官网公告弹窗**：每次访问自动弹出公告，显示近期重要更新

## v6.2.5 (2026-07-06) — AI 报告降级修复 + Worker 重部署 + 官网修复

### 🐛 Bug 修复
- **AI 报告显示金句而非数据**：`_call_ai()` 所有上游失败时 fallback 返回 `{'ok': True}` + 随机金句，导致 `generate_report()` 误判成功直接显示金句。修复为返回 `{'ok': False}`，让报告走本地数据摘要路径（学习时长、轮次、复盘记录等）
- **Cloudflare Worker 未部署**：`/api/ai-proxy` 返回 404，AI 服务完全不可用。重新部署 Cloudflare Pages Functions 恢复 AI 代理
- **关终端导致应用退出**：Python 进程前台启动，终端关闭时被杀。改用 `Start-Process -WindowStyle Hidden` 完全脱离终端
- **官网 Contact 等页面 404**：Next.js 静态导出生成 `contact.html`，但 Cloudflare Pages 需要 `contact/index.html`。添加 `fix-routes.js` 构建后脚本自动修复目录结构

## v6.2.4 (2026-07-06) — AI 报告反幻觉修复

### 🐛 Bug 修复
- **AI 报告胡话修复**：system prompt 和 user prompt 均加入"禁止编造数据中不存在的信息"约束，AI 不再编造老师姓名、学校、科目细节等虚构内容，所有结论必须引用具体数字

## v6.2.3 (2026-07-06) — 官网功能完善

### 📧 Contact 页
- 新增 `/contact` 页面：邮箱 + 微信二维码 + GitHub Issue 模板链接
- 替代原来无效的 mailto 链接

### 📋 GitHub Issue 模板
- 新增 bug_report.md / feature_request.md / partnership.md 3 个模板
- 用户提交 Issue 时自动选择类型

### 📚 文档页产品简介
- docs 页面新增「Rest Reminder 是什么」介绍段
- 4 个数据卡片（48MB / 60min / 17 徽章 / MIT）
- 右侧 TOC 新增「产品简介」锚点

### 🧭 导航栏 + Footer 更新
- Navbar 新增「联系我们」链接
- Footer "联系我们" 栏改为指向 Contact 页

### 📖 README badges
- 新增 Stars + Platform badges
- 新增 Contact 链接

## v6.2.2 (2026-07-06) — 官网全面改版

### 🎨 官网视觉升级
- 页面背景：纯白 `#ffffff` → 暖奶油色 `#fdf6f0`，长时间浏览不伤眼
- 全套暖色系配色：文字 `#2d2420`、边框 `#e0d5ca`、surface `#f5ece3`
- CTA 横幅：冷灰色 → 深棕渐变（`#3d2b20` → `#7a5240`），白字清晰
- 底部粘性 CTA 栏：半透明白 → 深棕色 95% 不透明

### 🧭 导航栏改版
- 新增"定价"链接
- 新增搜索按钮（链接到文档搜索框）
- 文字颜色适配深色导航栏（白色）

### 📄 Footer 重设计（WorkBuddy 风格）
- 顶部 Hero CTA：「保护你的眼睛，从每一次休息开始」+ 下载按钮
- 4 栏导航：服务条款 / 文档指引 / 产品下载 / 联系我们
- 暖金色圆点标记 + hover 高亮

### 📚 文档页三栏布局（WorkBuddy 风格）
- 左侧导航（已有）+ 中间内容（800px）+ 右侧"快速导航"
- 右侧 TOC：13 个锚点链接，滚动自动高亮当前章节
- 顶部搜索框：输入关键词按 Enter 跳转匹配章节

### 🧹 知识库清理
- 删除 7 个过期/冗余文件
- AGENTS.md / CLAUDE.md 移除过期引用
- 新增 7 条 .learnings/ + 5 条 CLAUDE.md 踩坑警示

## v6.2.1 (2026-07-06) — 官网视觉修复

### 🎨 官网背景色
- 页面背景从纯白 `#ffffff` 改为暖奶油色 `#fdf6f0`，长时间浏览不伤眼
- CTA 横幅从冷灰色渐变改为深棕色渐变（`#3d2b20` → `#7a5240`），白字清晰可见
- 底部粘性 CTA 栏从半透明白改为深棕色 95% 不透明

### 🐛 Navbar 文字修复
- 导航栏 "Rest Reminder" / "文档" / "GitHub" 文字颜色从 `var(--fg)`（深棕）改为白色，深色导航栏上清晰可见

### 🧹 知识库清理
- 删除 7 个过期/冗余文件：handoff.md、TODO-v4.3.md、产品规格-v4.3.md、优化审查报告、release-notes ×2、项目进度.md
- AGENTS.md / CLAUDE.md 移除过期引用，修正 tray_card.py 描述
- 新增 7 条 .learnings/ 经验记录 + 5 条 CLAUDE.md 踩坑警示

## v6.2.0 (2026-07-06)

### 🐛 主界面文字乱码修复
- **根因**：9 处 `QFont()` 调用把 CSS 风格逗号分隔串（如 `'Georgia, "Noto Serif SC", serif'` 或 `'Consolas, "SF Mono", monospace'`）当作字体名单名字传入。QFont 不认识这种分隔，整个字符串匹配失败回退到系统默认字体 → 中文字符 moji-bake / 方块 / emoji 不渲染
- **修复**：所有 `QFont` 调用改为只用单一主字体名（`Georgia` / `Consolas` / `Microsoft YaHei` / `Segoe UI Emoji`），fallback 留给 Qt 字体链接表自动处理。涉及 rest-reminder.py L776/L3642/L4029/L4425/L4555/L5034/L5992/L6215/L6346 共 9 处
- **扫描**：同步扫描整棵项目其他潜在乱码元凶（JSON 读写编码、subprocess stdout 解码、邮件 MIME、HTML charset、BOM）—— 全部确认为 UTF-8 无误

### 🔧 飞书日历 lark-cli 路径亡址修复
- **根因**：`C:\Users\binlo\.workbuddy\` 已被删除，但 `.settings.json` 里 `lark_cli_path` 仍指向该亡址，导致"未安装 lark-cli 或不在 PATH"错误
- **修复**：改为 npm 全局路径 `C:\Users\binlo\AppData\Roaming\npm\lark-cli.cmd`（已验证 v1.0.65 可用）

### 🤖 AI 服务超时 fallback 修复
- **根因**：内置 Cloudflare Worker 代理（`crazy-rest-reminder.pages.dev`）在大陆经常 30 秒超时，`_call_ai()` 直接 return `ok=False` + 错误字符串 → UI 显示"所有 AI 服务暂时不可用"错误 toast，review 报告不可用
- **修复**：所有上游都失败时，从本地 `.wisdom_quotes.json`（9 条狂客智慧语录）fallback 一条内容继续显示。**用户体验：超时 → 显示本地金句，不再弹窗报错**
- 注：链路通畅瞬间仍能拿到真实 AI 输出

### 📄 官网新增法律合规页面
- 新增 `pricing`（定价）、`privacy`（隐私政策）、`rules`（社区规则）、`terms`（服务条款）4 个独立页面
- 为后续合规上架准备基础框架

## v6.1.9 (2026-07-04)

### 🎯 浮球 popup 飞书日程显示修复
- 根因：`_show_info_popup()` 中 root QFrame 及所有子控件创建代码缩进错误，不在 `if popup is None:` 块内，导致每次点击浮球都重建整个 UI 树，旧 root 遮挡新内容，日程标签无法正常显示
- 修复：将 UI 构建代码缩进进 `if popup is None:`，真正实现首次创建、之后复用
- popup 高度 220→240，给日程留更多空间

### 🔄 版本更新检查
- 启动 3 秒后后台静默检查 GitHub releases 最新版本
- 本地版本低于最新版时弹窗提示用户更新（置顶显示）
- 手动点击「检查更新」也可触发（非静默模式）

### 🐛 稳定性修复
- 补全 `import threading`：3 处 `threading.Thread` 调用但从未导入，导致 AI 报告生成和版本检查崩溃

## v6.1.8 (2026-07-04)

### 🐛 浮球卡片空白修复
- 关闭 popup 后再点击浮球打开时卡片内容空白：`_show_info_popup()` 默认文字刷新和 `_update_popup_text()` 在 `if popup is None:` 块内，关闭后再次点击跳过文字刷新。移到块外，确保每次显示都执行

### 📖 文档站 /docs 全面改版与修复
- Claude.ai 风格改版：浅色背景 + 左侧导航 + 卡片式内容，三栏布局
- 导航链接修复：DocsNav 中 `#60分钟循环` → `#专注循环`
- 补充导航入口：界面预览、设置详解、故障排除
- TOC 双层包裹清理
- 全局样式隔离：`[id] scroll-margin` → `.docs-main [id]`
- 死代码清理：`.docs-prose` / `.step-number` / `.flow-arrow`
- 硬编码颜色统一：`<pre>`/`<code>` 背景 → `var(--surface)`
- 底部导航文案修正：「下一页」→「回到顶部」

## v6.1.7 (2026-07-04)

### 🐛 崩溃修复
- **import copy 缺失**：`LocalSync.save_settings` 使用 `copy.deepcopy` 但文件未 `import copy`，触发 NameError（crash.log 2026-07-03 17:54）。补充 `import copy`
- **复盘弹窗 QSlider GC**：`_build_review_dialog` 设了 `WA_DeleteOnClose`，`exec_()` 返回时 C++ 对象已销毁，自动提交或手动提交后访问 `_score_slider.value()` 报错。移除 `WA_DeleteOnClose`，在 `_prompt_review` 中安全取值

### 🧹 代码清理
- **`_enter_rest()` 重复代码**：移除重复的 `log.info` + `tray_icon.showMessage`，保留一份

### 📖 文档同步
- **CLAUDE.md**：行号从 4413 更正为 8127；AI 系统从"SenseNova + Agnes 双 API"更新为"任意 OpenAI 兼容 API + fallback"
- **`产品规格-v4.3.md`**：头部添加弃用声明，标记为历史文档与当前 v6.1.6 脱节
- **关于页**：动态展示真实 `ai_providers` 列表（name/model/priority/status），兼容 legacy SenseNova/Agnes key
- **诊断窗口**：更新 AI 状态检测逻辑，优先展示 providers 数量而非 legacy key

### ⚡ 性能
- **设置保存防抖**：28 处 `LocalSync.save_settings` 同步直调，连续勾选/拖动滑块时高频写磁盘。改为 class-level QTimer 300ms 防抖，多次调用合并为一次写入；`quit_app` 前 `flush_pending_settings` 确保落盘

### 🧹 死代码清理
- **单实例锁 msvcrt 文件锁残留删除**：`_file_lock_check`/`_cleanup_file`/`_lock_handle`/`_lock_path`/`import msvcrt` 全部删除。Windows Named Mutex 是内核级可靠方案（崩溃自动释放、无竞态），文件锁是死代码且 `msvcrt.locking` 有竞态。Mutex 失败时降级为"允许启动"（宁可多开也不误拦）

### 🛠 健壮性
- **飞书日程 subprocess 不可中断**：`subprocess.run` 改 `Popen + communicate`，`cancel()` 里 `proc.terminate()/kill()`，stop() 时能立即终止子进程，不再等到 30s timeout
- **飞书日程缓存默认值 24h → 1h**：`refresh_interval` 默认 86400 → 3600，避免跨天后今日日程不刷新（调用方仍可覆盖）
- **3 处 `except Exception: pass` 加 log**：`FloatingBall.hideEvent/showEvent` 加 `log.warning`，趋势时段评分解析加 `log.debug`，便于诊断

## v6.1.5 (2026-07-03)

### 🐛 崩溃修复
- **邮件测试发送线程堆叠崩溃**：`_send_test_email` 连点会 new 多个 `_WeeklyReportWorker` 并发跑 agently-cli，旧 worker 既不 quit/wait 也不 deleteLater。改为发送前先 quit+wait(2000)+deleteLater 旧 worker，发送按钮 disable 防连点，回调首行 `sip.isdeleted(self)/sip.isdeleted(self._mail_status_lbl)` 守卫，主窗口关闭后回调安全返回
- **周报自动发送回调崩溃**：`_check_weekly_report` 的 lambda 直接调 `log.info`，无 `sip.isdeleted` 守卫。改为具名函数 + 守卫
- **JSONStore 并发写丢 key**：`storage.py` 的 `load`/`save`/`set` 无锁，后台报告线程读 `.stats_history.json` 与主线程写同一 store 时静默丢 key。新增实例级 `threading.Lock`，`set` 复合操作原子化
- **JSONStore 异常静默吞**：`load()` 原 `except Exception` 吞所有错误无日志。收窄到 `json.JSONDecodeError` + `OSError` 并 `log.warning` 记录路径与原因，便于排查

### 🎨 主题一致性
- **`md_to_html` 不接受 theme 参数**：报告 HTML、邮件 HTML 全硬编码 dark 色（`#252530`/`#d4af37`/`#e8e4dc`/`#18181f`/`#b8b4ac`），light 主题下报告视图仍是 dark 底色色块。`md_to_html(text, theme='dark')` 新增可选参数，颜色全部从 `THEMES` 字典取，AI 报告视图调用传 `self._current_theme`，跟随主题切换

### 🛠 健壮性
- **飞书 node 版本路径硬编码**：`feishu_calendar.py` 硬编码 `.workbuddy\binaries\node\versions\22.22.2\node.exe`，WorkBuddy 升级 node 后路径失效。改为 `glob` 动态匹配 `versions\*\node.exe` 取最新版本
- **托盘卡片版本号永远显示 v3.3**：`tray_card.py` `update_data` 默认 `version='v3.3'`，调用方未传时永远显示 v3.3（实际 v6.1.5）。改为尝试 `from rest_reminder import VERSION`，失败用占位
- **PyInstaller 残留 hiddenimport**：`RestReminder.spec` 含 `'backup'` 但 `backup.py` 已不存在，构建 warning。删除残留

## v6.1.4 (2026-07-02)

### 🐛 Bug 修复
- **修复飞书日程状态混淆**：`get_display_text()` 在获取失败时仍可能显示"今日无日程"，新增 `_fetch_failed` 状态标记与 `get_status()` 结构化接口，UI 明确区分"无法获取日程 / 正在同步 / 今日无日程 / 有日程"
- **修复飞书日程错误文案**：失败时主状态显示具体原因（lark-cli 未安装/超时/API 错误/解析失败），列表区同步显示用户友好的错误提示，不再出现"日程获取失败"与"今日暂无日程安排"同时出现的矛盾
- **修复复盘倒计时崩溃**：`_build_review_dialog` 和 `_show_round_goal_dialog` 中的 `_countdown` 定时器在对话框已关闭后仍尝试操作已销毁的 `QLabel`，添加 `sip.isdeleted` 防护
- **修复 AI 服务不可用**：`.settings.json` 中 `default_proxy.enabled` 被禁用后，`_init_ai_providers()` 不再回写修复结果，重启后仍不可用。改为返回修复后的 providers 列表，主构造函数同步回写 `self.app_settings['ai_providers']`。同时优化无可用提供商时的提示文案
- **修复设置页测试连接卡顿**：`_test_ai_provider()` 在主线程同步执行 HTTP 请求，导致点击"测试连接"时 UI 冻结。改为后台线程执行，结果通过 `QTimer.singleShot(0, ...)` 回主线程更新 UI，按钮测试中置灰避免重复点击

### 🎨 界面优化
- **数据卡片 redesigned**：`_make_stat_card` 从纵向 icon/value/title 改为横向圆形色块图标 + 数值/标题，视觉层次更清晰
- **状态卡片状态感知**：学习中/休息中/已暂停/待机使用不同主题色，状态文本加粗
- **倒计时卡片**："距离 22:00" 标题去除 emoji，剩余时间文本放大加粗
- **复盘摘要与连续打卡**：去除 emoji 依赖，改用文字标签与颜色区分最佳/最低
- **主题一致性**：主内容区 / 顶部栏 / tab 占位区 / QScrollArea 背景色改用 `THEMES` 变量，修复 light 主题下仍显示深色的硬编码问题
- **浮球弹出卡片扩容**：info popup 尺寸从 220×170 增大到 260×200，学习/轮次标签 9pt→8pt，按钮 30px→28px，缓解文字塞不下问题
- **22:00 倒计时改为倒计时模式**：进度条从正计时改为倒计时，4:30 满格(100%)，随时间推移逐渐减少到 22:00 时为 0%
- **飞书"刷新"按钮对比度修复**：文字颜色从 `#d0d0d0` 改为 `#f0f0f0` + 加粗，hover 更亮，解决看不清问题
- **侧边栏导航**：emoji 图标替换为 QPainter 矢量图标（今日文档、AI 神经网络、趋势折线、齿轮、信息圆圈），选中/未选中文字使用 text_primary 确保可读性
- **关于页按钮**：GitHub 按钮添加矢量图标，去除 emoji 前缀
- **托盘菜单样式增强**：增加 padding、圆角、选中态高亮，视觉更细腻
- **测试按钮样式增强**：hover/disabled 态更明显，交互反馈更清晰

### 🧹 交互优化
- **浮球点击切换显示/隐藏**：短点击浮球直接切换显示/隐藏，替代原来点击弹出 info popup
- **浮球右键菜单动态文案**：根据当前 visible 状态显示"👁 显示挂件"或"👁 隐藏挂件"
- **托盘菜单新增浮球切换**：右键托盘图标可快速显示/隐藏浮球，菜单文案自动同步当前状态
- **隐藏浮球后可从托盘恢复**：点击托盘菜单"⚡ 显示浮球"即可恢复，无需重启
- **成就卡片可点击查看详情**：每张成就卡片支持左键点击，弹出详情对话框展示名称、描述、解锁状态、当前进度/目标
- **AI 提供商优先级标识**：设置页 AI 卡片增加优先级徽章，priority=1 显示「⭐ 首选」，其余显示「备份 X」，明确调用顺序

### 🧹 代码清理
- 移除 `rest_reminder.py` 中重复的 `import tempfile`
- 移除 `_draw_sidebar_icon` 中多余的 `import math`（函数内）
- 版本号同步为 v6.1.4

---

## v6.1.3 (2026-07-02)

### 🐛 Bug 修复
- **修复计时漂移**：`datetime.now()` 差值导致长时间运行误差 5-10%，引入 `time.perf_counter()` 统一计时源
- **修复临时文件泄漏**：weekly HTML + ambient WAV 永久残留，引入 `_TempFileManager` 集中注册 + atexit 清理
- **增强日志归档**：按日期自动归档旧日志，避免 `rest_reminder.log` 无限增长

### 🌐 官网
- Sponsor 区重构：去除虚假赞助暗示，更新为真实技术生态（CC Switch、Kimi K2.7 Code）
- 文档 FAQ 新增赞助合作 4 条

---

## v6.1.2 (2026-07-01)

### 🐛 Bug 修复
- **修复趋势图完全空白**：v6.1.1 延迟加载重构后，`_switch_trend_period(7)` 和 `_load_heatmap_data()` 在 `return scroll` 之后，从未执行，导致趋势 tab 的柱状图、热力图、时段评分分布全部空白
- 初始数据加载移到 `return scroll` 之前

## v6.1.1 (2026-07-01)

### 🐛 Bug 修复
- **修复设置 Tab 显示趋势内容**：v6.1.1 延迟加载用 `removeWidget` + `addWidget` 导致 QStackedWidget 索引错乱，后续所有 Tab 内容错位
- 所有 `_build_xxx_tab` 改为 `return scroll` + `insertWidget(idx, widget)` 保持索引正确

### 🌐 官网
- 下载安装步骤配图从右键菜单换成 GitHub Releases 页面截图

---

## v6.1.0 (2026-07-01)

### ⚡ 性能优化
- **启动速度**：非首屏 Tab 延迟加载（AI报告/趋势/设置/关于），启动只构建"今日"，切到时才构建
- **趋势图缓存**：QPixmap 缓存柱状图和热力图，数据不变时直接复用，避免每次 paintEvent 重绘

### ✨ 体验优化
- **飞书日程手动刷新**：今日 Tab 日程卡片加 🔄 刷新按钮，不用等 24 小时
- **复盘记忆学科标签**：下次复盘自动选中上次选择的学科和标签
- **AI 报告强制刷新**：报告区加"🔄 强制刷新"按钮，忽略缓存重新生成
- **护眼提醒跳过**：20-20-20 浮窗加"跳过"按钮，不想等 20 秒可直接关闭

---

## v6.0.2 (2026-07-01)

### 🐛 Bug 修复
- **修复成就不解锁**：启动时静默检查历史数据，自动解锁已达标但未触发的成就（不弹 Toast 避免轰炸）
- **飞书日程改为每天获取一次**：从每 5 分钟改为每 24 小时，减少 99.6% 的 lark-cli 调用
- **飞书日程失败重试**：获取失败时 10 分钟后自动重试，最多 3 次

---

## v6.0.1 (2026-07-01)

### 🐛 Bug 修复
- **修复飞书日程获取失败**：`subprocess.run(text=True)` 在 Windows 上默认 GBK 解码，lark-cli 输出 UTF-8 中文日程名时解码失败 → stdout 变 None → JSONDecodeError。加 `encoding='utf-8'` 修复
- **增强错误诊断**：returncode=0 但 stdout 为空时也重试，不再直接 JSONDecodeError 崩溃
- **popup 日程简写**：浮球 popup 中的飞书日程改为简写格式（`起床 04:30-04:35`），不再显示冗长的"还有X分钟结束"

---

## v6.0.0 (2026-06-30)

### 🪟 主界面行为修复
- **去掉主界面置顶**：`WindowStaysOnTopHint` 移除，主界面不再永远挡在最前
- 对标正常产品（微信/QQ音乐/Stretchly）：大窗口不置顶，小挂件/浮层置顶
- 浮球/popup/休息浮层/护眼浮层保持置顶不变
- 副作用：去掉置顶可能缓解之前卡顿（Windows 不再持续维护 Z 序）

### 🤖 AI 服务自定义提供商
- **支持任何 OpenAI 兼容 API**：不再局限于 SenseNova/Agnes，可添加 DeepSeek/Kimi/通义/智谱等
- **设置 Tab 全新 UI**：每个提供商独立卡片（名称/URL/模型ID/API Key/启用开关/测试连接/删除）
- **测试连接按钮**：发一个简单 prompt 验证，15秒超时，显示返回内容或错误
- **优先级机制**：多个提供商按顺序尝试，前一个失败自动切下一个
- **内置免费 AI（Cloudflare 代理）**：开箱即用，key 隐藏在 CF Pages secrets 中，用户看不到
  - 代理 URL：`https://crazy-rest-reminder.pages.dev/api/ai-proxy`
  - 限流：每 IP 每天 30 次
  - model 白名单：只允许 auto/sensenova-6.7-flash-lite/agnes-2.0-flash
  - 多上游 fallback：SenseNova → Agnes
- 用户可自配 provider 追加，默认 provider 保留作为 fallback
- API Key 加密存储复用 `_encrypt_key`

---

## v5.9.0 (2026-06-30)

### 🤖 AI 报告修复
- **错误信息透明化**：`_call_ai` 改为收集每个端点（SenseNova/Agnes）的错误，最终拼接显示，不再只显示最后一个
- **降级报告显示错误详情**：本地降级报告末尾追加具体错误（哪个服务、什么错误），方便用户诊断
- **业务错误提取**：HTTP 非 200 时优先解析 `error.message` 字段，避免显示原始 JSON

### 🏅 成就功能优化
- **扩充成就**：16 → 19 个，新增「一周巅峰」（单周30h）、「月度学霸」（单月100h）、「反思大师」（100次复盘）
- **进度条修复**：硬编码 `fill_pct * 5.0` → QProgressBar 自适应宽度，窗口缩放不再错位
- **百分比显示**：`5/16` → `5/19 · 26%`，进度一目了然
- **差额提示**：未解锁成就显示「差 Xh · 30%」，知道还差多少
- **今日解锁金边**：今天解锁的成就卡片加 2px 金色边框 + 高亮背景，视觉强调
- **Toast 延长**：解锁通知 5s → 8s
- **全成就彩蛋**：19/19 达成时显示「👑 全成就达成！你是真正的学习王者」
- **网格自适应**：每行最多 4 个，超出自动换行，窄屏不再挤压

---

## v5.8.0 (2026-06-30)

### 💾 GitHub 自动备份
- **每24小时自动备份**：学习记录/复盘记录/设置/连续打卡/历史统计 → GitHub 私有仓库
- **设置 Tab 新增备份区**：GitHub Token + 仓库名配置、验证连接、手动备份、恢复数据（带确认对话框）
- **恢复数据后提示重启**：覆盖本地文件后提示重启应用以加载
- **Token 加密存储**：与 AI Key 共用机器级 XOR 加密，不存明文
- **backup.py 模块**：独立备份/恢复/验证，`requests` 调用 GitHub API，无需 git 依赖

### 🌐 官网优化
- **Footer 去重**：删除页脚重复的「技术支持」赞助商栏（仅在赞助商区块展示）
- **文档页优化**：新增面包屑导航（首页 → 文档）+ 底部翻页导航
- **修复视频路径**：Hero 视频引用 `rest_reminder_promo.mp4` → `promo_video.mp4`

---

## v5.7.0 (2026-06-30)

### 🎨 视觉升级（攒流量前优化第一弹）

#### 浮球重绘
- **矢量图标取代 emoji**：自绘 QPainterPath 闪电（学习态）/ 暂停符号（休息态），保证所有 Windows 机器渲染一致，不再依赖字体
- **径向渐变底**：QRadialGradient 光源偏上模拟"能量球"质感，取代纯色 #141418
- **进度环线性渐变**：琥珀(#d4a853)→亮金(#f0c870)渐变，取代纯色
- **半透描边柔光**：QColor(212,168,83,90) 模拟光晕
- 学习/休息态形成"播放/暂停"语义对比

#### 侧边栏 logo 矢量化
- **消除 emoji 依赖**：侧边栏 logo 从 `QLabel('⚡')` + emoji 字体改为 QPixmap 渲染矢量闪电 path，与浮球图标完全一致
- 产品内不再有任何 emoji UI 依赖，跨机器渲染统一

#### info popup 主题感知
- **info popup 跟随主题变色**：新增 `_apply_popup_theme()` 方法，统一应用主题色到 popup 背景/边框/计时器/目标/轮次/日程/按钮。点击浮球弹出 popup 时调用，主题切换后下次弹出自动刷新
- 修复 light 主题下 popup 仍显示深色（硬编码 rgba(20,20,24,235)）的问题
- action 按钮从硬编码蓝色 #3b82f6 改为主题 accent 色，与整体视觉体系统一

#### 空状态设计（新用户留存）
- **趋势图空状态**：纯文字"暂无数据" → 矢量闪电图标（淡化 22% 透明度）+ "开始第一次学习，趋势图会在这里生长" 引导文案，适配主题色
- **AI 报告空状态**：新用户无数据时不再调 AI（避免返回"暂无记录"），直接显示引导："还没有学习记录 → 完成第一次 60 分钟学习后 AI 会在这里为你生成个性化报告"
- **复盘空状态**：去掉 emoji 📭 依赖，改为纯文字引导，补充"学习一轮后会自动弹出"的行动提示
- 消除 3 处 emoji UI 依赖（📭），与浮球/logo 矢量化一致

#### 主题系统修复
- **修复 light 主题不生效**：`init_ui` 硬编码 dark 样式作底 + theme_stylesheet 覆盖的叠层机制，light 主题时部分元素仍显示 dark。改为直接用 `_apply_theme_stylesheet()` 生成，dark/light 一致
- **修复 `_switch_theme` 叠层残留**：切换主题时 base_sheet 仍含硬编码 dark，改为直接 `setStyleSheet(self._theme_stylesheet)`
- 消除 ~65 行硬编码样式与 THEMES 系统的重复维护债

---

## v5.6.7 (2026-06-30)

### ✨ 新增
- **官网首页宣传视频**：Hero 区添加 AI 生成的产品宣传视频背景（自动播放/静音/循环），暖色调电影质感呈现"专注→提醒→休憩→重启"核心叙事

---

## v5.6.6 (2026-06-30)

### 🐛 Bug 修复
- **修复飞书日程间歇性获取失败**：`_FetchWorker` 在 lark-cli 返回非零时无重试且错误信息只取 stderr（丢失 stdout）。改为：失败后等待 2 秒重试一次（应对 token 刷新窗口/网络瞬断），错误信息同时记录 stdout + stderr（消除诊断盲区）

---

## 📝 文档更新 (2026-06-30)

### 📄 开发知识沉淀
- **CLAUDE.md 新增「核心工作原则」**：第一性原理（动手前验证假设、根因优先）、对抗性审查（交付前三维度自查）、验证实际运行（crash.log 优先、重复指令=未生效信号）、穷尽方案再求助
- **补充踩坑记录**：
  - PyQt5 多实例防护：`kernel32.CreateMutexW + GetLastError==183`（取代有竞态的 `msvcrt.locking` 文件锁，原子操作 + 崩溃自动释放）
  - Win11 任务栏图标丢失：`FramelessWindowHint + WindowStaysOnTopHint` 导致图标消失，`showEvent` 中用 ctypes 设 `WS_EX_APPWINDOW`
  - SenseNova 推理模型：`sensenova-6.7-flash-lite` 的 `content` 可能为空，回复在 `reasoning` 字段，需 `max_tokens >= 4096` 并 fallback
  - 飞书日程 `CalendarManager` 初始化顺序：必须在 `init_ui()` 前初始化
  - pythonw 下 PATH 不完整：用 `shutil.which` 或绝对路径找 `lark-cli.cmd`
- **AGENTS.md 同步**：关键踩坑列表补充 v5.4.0 经验
- **.gitignore**：新增 `.workbuddy/` 忽略规则

> 本次为纯文档更新，不影响应用功能。

---

## v5.6.5 (2026-06-30)

### ✨ 新增
- **首次引导（Onboarding）**：新用户启动时显示 3 页引导弹窗（浮球操作 → 60+5 循环 → AI 复盘与报告），存 `onboarding_shown` 标志避免重复
- **主题即时切换**：切换主题后立即生效，无需重启应用
- **删除快捷键功能**：移除所有全局快捷键（Ctrl+Alt+P/S/B 和 Ctrl+1-5）

### 🐛 Bug 修复
- **修复倒计时浮层崩溃**（v5.6.4 已修）
- **修复快捷键崩溃**（v5.6.4 已修，本次删除快捷键彻底移除）
- **修复 20-20-20 护眼从未生效**（v5.6.4 已修）

---

## v5.6.4 (2026-06-30)

### 🐛 Bug 修复（对抗性审查验证）
- **修复倒计时浮层崩溃**：`CountdownOverlay` 访问不存在的 `self.app_settings`，改为从 `main_window` 获取
- **修复快捷键崩溃**：`Ctrl+Alt+B` 调用未定义的 `_enter_rest()`，已补全方法
- **修复 20-20-20 护眼从未生效**：`EyeRestOverlay.show_reminder()` 没有任何调用代码，已在 `update_display` 中添加每 20 分钟触发逻辑

---

## v5.6.3 (2026-06-30)

### ✨ 功能
- **飞书日程集成**：lark-cli v1.0.60 已安装并授权，设置页开启后显示今日日程

---

## v5.6.2 (2026-06-30)

### 🎵 白噪音重写
- **Voss-McCartney 粉红噪声算法**：1/f 频谱，听起来更自然
- **立体声**：左右声道不同随机状态，空间感更好
- **dithering**：减少 16bit 量化失真

### 🐛 Bug 修复
- **agently-cli `--body-file` 路径**：必须使用相对路径 + `cwd` 参数
- **设置界面 Toast**：所有按钮/开关点击后弹出"已保存配置"提示

---

## v5.6.1 (2026-06-30)

### 🐛 Bug 修复
- **修复 3 个设置开关无效**：声音提醒/复盘弹窗/学习时长统计的 toggle 开关实际不生效，现已正确响应设置
- **修复成就永远无法解锁**：`rounds_10/50/100` 成就因 `save_daily_stats` 缺少 `rounds` 字段永远为 0
- **修复学习时长丢失风险**：学习时长改为进入休息时立即记录，不再等到休息结束（防止崩溃丢失）
- **修复 QThread 信号名冲突**：`_WeeklyReportWorker`/`_ReportWorker` 的 `finished` 信号覆盖 QThread 内置信号，改为 `result_ready`
- **修复成就 Tab 崩溃**：`QGridLayout` 未导入导致成就卡片展示时 NameError
- **修复 PyInstaller 打包**：`RestReminder.spec` 补充 `tray_card`/`feishu_calendar` hiddenimports
- **更新 AGENTS.md**：关键文件列表补全 `tray_card.py`/`feishu_calendar.py`

---

## v5.6.0 (2026-06-30)

### 🎨 体验优化
- **成就显示重构**：卡片式展示（icon + 名称 + 进度文本），未解锁成就显示当前进度（如 `12/50h (24%)`），已解锁显示解锁日期；顶部总进度条
- **环境白噪音优化**：音频时长 10s → 30s，首尾 0.5s crossfade 消除循环断裂；`array.array` + 分块 `struct.pack` 批量写入，生成性能提升 100×；缓存大小校验避免旧版本残留
- **关于界面字体放大**：环境检测 / 数据文件 / AI 服务状态 11px → 13px，状态点 8px → 10px，深色背景下清晰可读

### 📧 邮件周报
- **改用 Agent QQ 邮箱**：通过 `agently-cli message +send` 发送（subprocess 调用），移除 SMTP 服务器 / 账号 / 授权码配置；设置页只保留收件人邮箱；两阶段确认令牌自动完成

---

## v5.5.0 (2026-06-29)

### 🆕 新功能
- **成就/徽章系统**：16 个成就（学习时长 / 连续打卡 / 复盘质量 / 轮次里程碑），解锁 Toast 通知，「关于」tab 集中展示
- **GitHub 风格学习热力图**：52 周 × 7 天，5 级颜色梯度，hover 显示具体日期与学习时长
- **环境白噪音**：5 种程序生成音效（雨声 / 森林 / 咖啡厅 / 白噪音 / 棕噪音），独立音量控制，启动自动恢复上次状态
- **每周邮件周报**：SMTP 配置（QQ / 163 / Gmail / 飞书），HTML 格式 AI 学习报告，周一 09:00 自动发送
- **主题切换**：深色 / 浅色 / 跟随系统，「设置」tab 下拉选择，重启生效
- **全局快捷键**：`Ctrl+Alt+P` 暂停/继续、`Ctrl+Alt+S` 静音、`Ctrl+Alt+B` 显示浮球、`Ctrl+1~5` 切换 Tab
- **统一 Toast 通知入口**：所有成就解锁、状态变更、错误提示统一走 `_show_toast()`，风格一致

### 🔒 安全与体验
- **API Key 加密存储**：XOR + base64 + 机器盐值，向后兼容明文旧配置

---

## v5.4.0 (2026-06-29)

### 🆕 新功能
- **飞书日程集成**：新增 `feishu_calendar.py` 模块，后台拉取飞书日程，「今日」tab 实时显示当前/下一日程
- **趋势时间选择器**：近7天/14天/30天/自定义日期范围，柱状图和热力图同步刷新
- **AI API Key 配置界面**：「设置」tab 可直接输入 SenseNova / Agnes AI Key

### 🐛 修复
- **SenseNova 推理模型兼容**：max_tokens 4096 + reasoning 字段 fallback，解决 content 为空
- **Windows 任务栏图标丢失**：Win32 API 强制 WS_EX_APPWINDOW
- **多实例启动竞态**：改用 Named Mutex 内核级互斥锁，消除文件锁竞态条件
- **初始化顺序 bug**：FeishuCalendarManager 在 init_ui() 前初始化
- **lark-cli 路径问题**：pythonw 环境用 shutil.which 定位

### 🎨 界面优化
- 「关于」tab 重新设计：品牌 Hero 区 + 双栏环境/数据卡片
- 「趋势」tab 全面重构：渐变柱图、网格参考线、hover 详情
- 「设置」tab 新增飞书集成 + AI 服务配置区

## v5.3.0 (2026-06-29)

### 🐛 关键 Bug 修复（21 项）

**数据存储层**
- **P0** `JSONStore.load()` 返回共享可变默认值 → 改为 `copy.deepcopy()`，杜绝幽灵数据（`storage.py`）
- **P0** 日期切换时先 `save_daily_stats()` 再重置，防止学习时长数据丢失
- **P0** `app_state_store` 添加 `default={}` 防止文件不存在时 `FileNotFoundError`

**线程与并发**
- **P0** `_ReportWorker` 线程引用未存储 → 改为 `self._report_worker`，防止 GC 回收导致报告生成永久卡死
- **P0** 添加旧 Worker 取消逻辑，防止快速切换报告类型时并发执行
- **P0** `_fallback_check` 锁获取包裹 try/except，防止启动崩溃

**UI 崩溃修复**
- **P0** `mouseMoveEvent` 中 `drag_position` 为 None 时崩溃 → 添加 None 守卫
- **P0** `FloatingBall.mouseReleaseEvent` 中 `click_time` 为 None → 添加守卫
- **P0** `_bar_rects` 在首次绘制前被鼠标事件访问 → 预初始化为空列表（2 处）
- **P0** `quit_app` 遗漏 `eye_rest_overlay` 清理 → 添加 `hide_overlay()`
- **P0** `_info_popup` 的 `WA_DeleteOnClose` 导致 C++ 对象销毁后 Python 引用崩溃 → 移除

**逻辑错误**
- **P0** `_handle_running` 硬编码 `60 * 60` 忽略 `_activity_interval` → 改为动态计算
- **P0** 热力图数据源从 `history_store`（无小时分量，始终 hour=0）切换到 `review_store`（有 HH:MM 时间戳）
- **P0** 22:00 每日汇报中 `best`/`worst` 为 None 时直接下标访问 → 添加 None 守卫
- **P0** `_refresh_general_tab` 中 `time.time() - datetime` 类型错误 → 改为 `datetime.now()`
- **P0** 复盘对话框双重自动提交定时器 → 移除冗余的外部 `QTimer.singleShot`
- **P0** 复盘时间线评分条始终传 `is_old=False` → 改为 `info['is_old']`
- **P0** 距离 22:00 倒计时整点显示"60 分钟" → 改为从总秒数推导

**性能优化**
- `_refresh_general_tab` 缓存 `state_lbl`/`timer_lbl` 引用，避免每秒 `findChild()` 遍历控件树
- `StatsWindow.paintEvent` 缓存历史数据，避免每次重绘读取 JSON 文件
- 3 处动态 `paintEvent` 添加 `QPainter.end()` 防止资源泄漏
- `_sync_buttons` 弹窗隐藏时跳过无意义计算
- `setWindowOpacity` 闪烁动画添加 `sip.isdeleted` 守卫

**托盘卡片**
- **P0** `tray_card.py` 4 处 lambda 闭包 late-binding bug → 所有菜单项都触发 `export_data` → 改为默认参数捕获

**安全**
- `sensenova_vision.py` 移除硬编码 API Key，改为环境变量 `SENSENOVA_API_KEY`

---

## v5.2.0 (2026-06-28)

### 🐛 Bug 修复
- **P0** 修复 `This application failed to start because no Qt platform plugin could be initialized`：导入 PyQt5 前自动设置 `QT_PLUGIN_PATH` / `QT_QPA_PLATFORM_PLUGIN_PATH` 指向 `vendor/PyQt5/Qt5/plugins`，让 Qt 能找到 `platforms/qwindows.dll`
- **P0** 修复 `ModuleNotFoundError: No module named 'PyQt5'`：`rest_reminder.py` 顶部自动将 `vendor/` 加入 `sys.path`，开箱即用无需 `pip install`
- **P0** 新增 Python 版本守卫：非 3.14 启动时给出明确提示并退出（避免 vendor `.pyd` ABI 不兼容导致 `ImportError: cannot import name 'sip'`）
- **修复** 重启后连续打卡清零：`_restore_active_state` 末尾调用 `_check_streak`，跨重启 streak 不丢失
- **修复** 22:00 日报通知后窗口找不到：通知时自动 `show()` + `raise_()` + `activateWindow()`
- **修复** `_build_general_tab` 中 `streak_card` 重复创建（同一张卡片被实例化两次）
- **修复** `generate_report` 缓存写入失败时静默吞掉异常，改为 `log.warning` 输出错误

### 🎉 新增功能
- **趋势分析时段评分热力图**：12 个时段覆盖全天 0-24 时（0-2、2-4、4-6、…、22-24），按复盘数据的平均评分着色（绿=高分，黄=中等，红=低分），显示各时段复盘次数
- **浮球 popup 目标可点击**：浮球弹窗中 `🎯 未设目标` / 已设目标文本改为可点击按钮，hover 变色+下划线，点击直接弹出目标设置对话框

### 🗑️ 代码清理
- `_prompt_round_goal` 注释修正：自动提交时间从"3秒"改为实际值"60秒"

### 🎨 UI/UX
- **托盘/任务栏图标优化**：
  - `_create_app_icon()` 从 `cute_icon.png` 预生成 16/24/32/48/64/128/256 多尺寸 pixmap
  - `main()` 中设置 `QApplication.setWindowIcon()` + Windows `SetCurrentProcessExplicitAppUserModelID()`，让进程不再被任务栏识别为 python.exe
  - 新增 `休息提醒.lnk` 快捷方式，指向 `pythonw.exe` 并绑定 `cute_icon.ico`，双击启动即可在任务栏显示应用图标
  - `RestReminder.spec` 打包配置添加 `icon=['cute_icon.ico']`，生成的 EXE 任务栏图标正确

---

## v5.1.0 (2026-06-26)

### 🎉 重大改进
- **主界面全面实时刷新**：学习时长、当前轮次、休息时长、状态标签、22:00倒计时每秒更新（之前只显示启动时快照）

### 🐛 Bug 修复
- **P0** 修复复盘摘要空列表崩溃：无复盘数据时 best/worst 为 None 导致 TypeError
- **P1** 修复连续打卡恢复逻辑错误：历史恢复后 +1 重复执行，导致打卡数字跳变
- **P1** 修复月趋势周聚合越界：未来日期周未过滤，可能包含未来数据
- **P1** 修复季/年趋势统计天数不匹配：总览只展示最近6个月但统计用全量月份

### 🗑️ 重构
- 删除死代码 `_show_ai_report`（~90行，已被 _build_ai_tab 取代）
- 移除 frameless 窗口下失效的"最大化"按钮
- 修复右键菜单 emoji 渲染异常

## v5.0.1 (2026-06-26)

### 🐛 Bug 修复
- **修复** AI 日报日期范围：日报只统计今天（之前统计昨天+今天）
- **修复** `_md_to_html` Markdown 表格渲染：AI 输出的 `| 表头 |` 表格正确渲染为 HTML
- **修复** 托盘卡片新增「🎯 设定今日目标」入口（运行中随时重设）

### 📝 文档
- 行号修正：rest_reminder.py 4360→3836→4413 行（最终 4413）

---

## v5.0.0 (2026-06-25)

### 🎉 新增功能
- **柱状图悬浮提示**：鼠标移到趋势分析任意柱子即可看到具体学习时长数值
- **复盘学科新增「其他」**：支持复盘/健身/阅读/考试等非学科场景
- **AI 报告后台线程**：QThread 异步生成，不再阻塞 UI

### 🐛 Bug 修复
- **P0** 修复 AI 报告卡死：`_md_to_html` 定义在 `FloatingBall` 类中，`RestReminderWidget` 调用时抛 `AttributeError`，报告界面永远停在"正在生成报告"
- **P0** 修复 StatsWindow tooltip 不显示：两个 `mouseMoveEvent` 定义互相覆盖，tooltip 处理器被拖拽处理器覆盖
- **P0** 修复 PyQt5 sip 导入兼容性：Python 3.14 下 `import sip` 失败，改为 `from PyQt5 import sip`
- **P1** 修复 QToolTip / QRect 未导入导致崩溃

### 🗑️ 重构
- **趋势分析全面重构**：彻底移除电脑使用时长统计（6处代码引用），改为纯学习时长单柱图
- **删除双柱图 + 饼图**：移除 `_draw_dual_bar` 和 `_draw_pie_chart`，统一使用 `_draw_single_bar`
- **清理所有 computer 引用**：删除所有 `computer` 数据字段和图例
- **浮球图标**：⏰ → ⚡
- **AI 错误处理优化**：区分网络请求异常和响应解析异常
- **代码质量**：移除冗余变量初始化、统一 `max_val` 计算方式

## v4.4.0 (2026-06-23)

### 🎨 UI 重构：5标签页主界面
- **今日**：直接展示学习时长、当前轮次、休息状态（含倒计时）、复盘摘要、连续天数
- **AI 报告**：日报/周报/月报/季报/年报 5个按钮直接展示，无需额外点击
- **趋势**：图表直接渲染（修复 paintEvent 不触发空白问题）
- **设置**：从今日页拆分出独立标签页，含开关自启/静默启动/关闭最小化/学习统计/复盘提醒/声音提醒
- **关于**：版本信息 + 开源声明

### 🗑️ 移除
- **Pro 订阅系统**：完全移除，所有功能免费可用
- `rest-reminder-pro/` 不再需要，AI 报告内联到主程序
- `tray_card.py`：旧版托盘卡片（已弃用）

### 🐛 Bug 修复
- **修复** `Qt.Popup` 浮层按钮不可点击（focus loss 自动关闭）→ 改用 `Qt.Tool | Qt.FramelessWindowHint`
- **修复** `closeEvent` 用 `hide_to_edge()` 导致关闭后无法重新打开 → 改用 `hide()`
- **修复** 5个 `_toggle_*` 回调只写内存不写磁盘 → 设置持久化到 `app_settings` + `LocalSync.save_settings()`
- **修复** 趋势图 `paintEvent` 赋值后不自动触发 → 显式调用 `.update()`
- **修复** PyInstaller exe 日志输出到 `%TEMP%/_MEI*/` 而非项目目录
- **修复**  stale 锁文件导致新 exe 无法启动
- **修复** `_clear_tab` / `_refresh_active_tab` WA_DeleteOnClose 后操作 C++ 对象崩溃
- **清理** 4个死函数、模块级 inline import 副作用

## v4.3.0 (2026-06-21)

### 🎯 核心变更：计时规则重构
- **v4.3 产品规格**：新增 `产品规格-v4.3.md` 完整记录
- **固定60分钟学习**：移除活动密度感知/空闲自动暂停，统一60分钟
- **5分钟请辨倒计时**：最后5分钟弹出浮层显示请辨金句
- **5分钟休息状态**：新增 `_handle_resting()`，休息期间显示 ☕ 倒计时
- **固定B站收藏夹URL**：休息后自动打开固定收藏夹（非随机）
- **每3轮护眼视频**：第3/6/9...轮休息后打开护眼视频 `BV14Y4y1N7PW`
- **复盘在休息期间弹出**：进入休息状态时弹出 1-100分 复盘（学科 + 标签 + 评分）

### 🗑️ 删除的功能
- 电脑使用3小时周期提醒（保留简单累计显示）
- 20-20-20 护眼浮窗
- 活动密度感知（空闲自动暂停）
- 随机视频选择（改为固定URL）
- 4个死函数：`get_bilibili_videos` / `open_random_video` / `_do_open_video` / `show_computer_usage_reminder`

### 🎨 UI 重构（v4.2延续）
- **挂件即主界面**：挂件点击显示倒计时+学习时长+电脑时长+开始/结束按钮
- **主窗口默认隐藏**：启动后只显示浮球，点击浮球打开主界面
- **ccswitch风格**：380×340 深炭黑+金色极简面板

### 🐛 Bug 修复
- **P0** 修复趋势分析数据丢失（`show_stats` 冗余写入）
- **P1** 修复 float→int（`setValue` 不接受 float）
- **P1** 修复 `_handle_running` 残留旧活动密度代码

## v4.2.0 (2026-06-21)

### 🎨 UI 重构
- **主窗口大面板**：参考 ccswitch 风格，从 400×580 2×2 卡片网格改为 380×340 纵向列表
- 顶部：22:00 大字倒计时 + 进度条
- 中部：学习倒计时（Consolas 32px）+ 电脑使用时长行
- 主按钮：▶ 开始学习 / ⏸ 暂停（更大更清晰）
- 底部：📊🤖⚙️ 工具按钮行 + 自启按钮
- 移除：打卡卡片、学习产出卡片、休息时长卡片（数据后台追踪，UI 不显示）

### 🐛 Bug 修复
- **P0** 修复 `show_stats()` 每次调用写 `save_daily_stats()` 导致数据丢失
- **P0** 修复设置对话框双重写入（`save_settings` + `_set_reminder_mode` 都调 `save_settings`）
- **P1** 修复 `_glow_timer` 无 parent 导致 GC 回收
- **P1** 移除 2 处冗余 inline import（QMessageBox 已在模块级导入）

### 📋 文档
- 删除 `Pro收费逻辑设计.md`（246行，产品决策已变）
- 清理 README Pro 绑定段落
- 更新 docs/ARCHITECTURE.md 设计系统（颜色/字体/尺寸）
- 更新 AGENTS.md 窗口尺寸配置

## v4.1.1 (2026-06-20)

### 🐛 Bug 修复
- **P0** 修复 TrendWindow 反复 crash（`'NoneType' object has no attribute 'deleteLater'`）— `_clear_tab` 加 `sip.isdeleted()` 检查，`_refresh_active_tab` 加 `AttributeError` catch
- **P0** 修复设置对话框 `NameError: save_btn` — 遗漏按钮定义导致点击设置即闪退
- **P0** 修复 AI 报告 `ModuleNotFoundError: pro_features` — 子目录模块路径验证
- **P1** 修复单实例锁文件 `Permission denied` — `cleanup()` tolerant 处理 Windows 文件锁定竞争
- **P1** 修复 12 处 `except Exception: pass` 反模式 — 全部改为 `log.error/warning(...)`
- **P1** 移除 5 处 `[LINE xxx]` 旧调试标记
- **P2** `excepthook` 补 `log.error`（之前只写 crash.log 不进日志文件）
- **P2** TTS API key 改为环境变量 `STEPFUN_API_KEY`

### 🔧 改进
- QTimer 统一加 parent（`QTimer(self)`），防止 GC 提前回收
- 呼吸灯 `_update_glow` 加 early return（未运行时直接返回，不 setStyleSheet）
- `showEvent`/`hideEvent` 管理呼吸灯 timer 生命周期

## v4.1.0 (2026-06-19)

### 🎨 设计重构
- **Claude 风格**：深炭黑背景 + 珊瑚色 accent + Inter 字体 + 极简线条
- 主窗口：去掉径向渐变光晕，改为纯色 + 1px 边框
- 卡片：border-radius 14→8px，毛玻璃→纯色
- 按钮：金色→珊瑚色，pause 橙色→冷灰
- 计时器：金色→冷白，Consolas→JetBrains Mono

### 🏗️ 架构改进
- **新增 `storage.py`**：统一 JSONStore 类，消除 5 处重复 JSON IO 代码
- **新增 `docs/ARCHITECTURE.md`**：系统架构、状态机、数据流、设计系统文档
- **新增 `.env.example`**：环境变量配置模板
- **RestReminder.spec**：添加 `hiddenimports=['storage']`，修复 exe 启动崩溃

### 🐛 修复（P0-P2）
- **P0** 修复 `update_computer_usage_display` 死方法（计算但不 setText）
- **P0** 修复 `_bilibili_dns_error_logged` 永不重置（WARP 恢复后静默失败）
- **P1** 修复呼吸灯 50ms 始终运行（隐藏时停止，节省 CPU）
- **P2** 添加 B站视频 5 分钟缓存（避免每次休息都请求网络）
- **P2** 3 小时提醒改为收藏夹随机视频（不再硬编码 URL）
- **P2** 清理 4 个死函数（`_load_goal`/`_save_goal`/`_load_quotes_used`/`_save_quotes_used`）
- **P2** 清理冗余 import + 死代码

### 📋 其他
- 清理 3.6MB 临时文件（搜索缓存、旧脚本、重复目录）
- 更新 AGENTS.md（修正过时引用）
- 更新 README.md（修复截图引用、更新项目结构）
- 更新 CLAUDE.md（合并踩坑记录、添加新规则）
- 新增 6 条 learnings + 2 条 errors 记录

## v4.0.0 (2026-06-18)

### 🎉 新功能
- **全新 2×2 卡片化主界面**：毛玻璃卡片布局（深黑+金色），4 个数据卡片一目了然
- **20-20-20 护眼提醒**：每 20 分钟轻量绿色浮窗提示看远处 20 秒，15 秒自动消失
- **活动密度感知**：连续活跃 10min+ 自动缩间隔到 45min，空闲 5min 自动暂停
- **趋势分析窗口**：5 标签页（今日复盘/周趋势/月趋势/季年趋势/时段分析）
- **请辨金句模式**：休息时展示 15 条思辨金句，每日不重复
- **里程碑金句**：连续打卡 1/3/7/14/30/60/90/365 天不同奖励文案
- **每小时复盘**：倒计时结束后弹出 1-5⭐ 自评，数据落盘到 `.review_log.json`
- **托盘卡片升级**：自定义 TrayCard 替代原生菜单
- **Pro 版精简**：仅保留 AI 学习分析一项付费功能（云同步/主题/导出等全部砍掉）

### 🔧 改进
- **移除看门狗**：watchdog.py 删除，注册表直启主程序，更稳定
- **启动闪烁消除**：先定位到屏幕右侧再显示
- **日志降噪**：B站 API 的 DNS 错误只记一次

### 🐛 修复
- 修复构建路径中文字符导致 Turbopack 崩溃

## v3.2.0 (2026-06-06)

### 🎉 新功能
- **用户可配置**：B站收藏夹、提醒视频、昵称（不再硬编码开发者账号）
- **推荐返利**：分享推荐码，双方各得7天免费Pro
- **订阅制Pro版**：19.9元/月，云同步+高级统计+自定义提醒+数据导出+多主题
- **设置页面**：右键菜单新增"⚙️ 设置"，可视化配置所有选项
- **升级弹窗**：展示微信收款码+设备码+推荐码，一步到位

### 🔧 改进
- Hook脚本重写：修复PreToolUse hook导致Write/Edit/Bash被阻断的问题
- 订阅验证：三级验证（Supabase云端 → 本地缓存 → 24小时离线宽容）
- 托盘菜单优化：顶部显示订阅状态，一键刷新

### 🐛 修复
- 修复 `check-mandatory-load.sh` JSON解析错误导致所有工具调用报错
- 修复 settings.json hooks配置损坏

## v3.1.0 (2026-05-28)

### 🎉 新功能
- 学习时长追踪 + 连续打卡
- 电脑使用时长监控（每3小时提醒）
- 暗黑奢华主题
- 小浮球常驻桌面（可拖动）
- 开机自启 + 崩溃自动重启（看门狗）
- 22:00 每日学习汇报

### 🔧 改进
- 跨重启状态续接（计时器、休息状态、播放记录）
- 数据本地持久化（.daily_log.json）

## v3.0.0 (2026-05-15)

### 🎉 初始版本
- 60分钟循环休息提醒
- B站收藏夹随机视频播放
- 护眼视频自动打开
- 电池充电状态监控
- 系统托盘菜单
