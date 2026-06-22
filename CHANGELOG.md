# 更新日志

所有重要版本更新记录。

## v4.4.0 (2026-06-23)

### 🎨 UI 重构：5标签页主界面
- **今日**：直接展示学习时长、当前轮次、休息状态（含倒计时）、复盘摘要、连续天数
- **AI 报告**：日报/周报/月报/季报/年报 5个按钮直接展示，无需额外点击
- **趋势**：图表直接渲染（修复 paintEvent 不触发空白问题）
- **设置**：从今日页拆分出独立标签页，含开关自启/静默启动/关闭最小化/学习统计/复盘提醒/声音提醒
- **关于**：版本信息 + 开源声明

### 🗑️ 移除
- **Pro 订阅系统**：完全移除，所有功能免费可用
- `rest-reminder-pro/` 不再需要，AI 报告通过 `pro_features` 直接调用
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
