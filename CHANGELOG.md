# 更新日志

所有重要版本更新记录。

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
