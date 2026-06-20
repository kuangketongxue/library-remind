# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260618-001] correction

**Logged**: 2026-06-18T15:00:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
搜索工具必须全部源并行使用，不挑不筛

### Details
用户多次纠正搜索规则：
- zhihu-search 和 global-search 共用同一个 API KEY 但搜索不同内容源，两个都要用
- tavily 有2个key，但一次只用一个，主key额度用完才切备用key
- firecrawl 旧key是本月额度用完了，下月自动刷新，不是永久停用
- firecrawl keyless 免密钥版每月1000额度，当前使用此源
- opencli 小红书搜索也是可用源
- 所有源必须并行启动，不能串行

### Suggested Action
已创建完整指南: memory/experience-search-mandatory-all-sources.md
已更新 MEMORY.md 和 REFERENCE.md

### Metadata
- Source: user_feedback
- Related Files: memory/experience-search-mandatory-all-sources.md, memory/MEMORY.md, memory/experiences/REFERENCE.md
- Tags: search, parallel, mandatory

---

---

## [LRN-20260610-001] best_practice

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
Extract shared base class when multiple PyQt5 overlay widgets share drag/position/eventFilter code.

### Details
CountdownOverlay and EyeRestOverlay both implemented identical: `_drag_offset` tracking, `eventFilter()` for child-widget drag forwarding, `_load_position()` / `_save_position()` with JSON persistence. ~60 lines duplicated. Extracted `DraggableOverlay(QWidget)` base class.

### Suggested Action
When creating new overlay widgets in this project, inherit from `DraggableOverlay` instead of reimplementing drag/position logic.

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`
- Tags: code-reuse, pyqt5, refactor
- Pattern-Key: reuse.overlay_base_class
- Recurrence-Count: 1
- First-Seen: 2026-06-10
- Last-Seen: 2026-06-10

---

## [LRN-20260610-002] best_practice

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
Consolidate scattered reset logic into a single `_reset_X()` method when the same state is reset in 3+ locations.

### Details
Eye rest timer state (`eye_rest_elapsed`, overlay hide) was reset in 3 places with copy-pasted code: timer-end, date-change, and break-start. Extracted `_reset_eye_rest()` called from all 3 sites. Also removed dead state `_eye_rest_countdown_active` (written 4 times, read 0 times).

### Suggested Action
Before adding reset logic, check if a reset method already exists. If resetting the same state in 2+ places, extract a method immediately.

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`
- Tags: code-simplification, dead-state
- Pattern-Key: simplify.scattered_reset
- Recurrence-Count: 1
- First-Seen: 2026-06-10
- Last-Seen: 2026-06-10

---

## [LRN-20260610-003] knowledge_gap

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Netlify CLI deploy times out on network issues; direct API curl upload is a reliable fallback.

### Details
`npx netlify deploy --prod --dir=out` failed with ConnectTimeoutError. Direct `curl -X POST` to Netlify API with zip upload worked (auth token valid, just CLI network issue). However, account credits can still block deploys at the API level.

### Suggested Action
For future deploys, use curl API approach as primary method since CLI has network issues. Check account credits first.

### Metadata
- Source: error
- Related Files: `rest-reminder-site/netlify.toml`
- Tags: netlify, deploy, fallback
- See Also: ERR-20260610-002

---

## [LRN-20260610-004] correction

**Logged**: 2026-06-10T23:55:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
User said "更新网站和GitHub开源项目" — I deployed the personal site to CF Pages instead of the rest-reminder site. User corrected: "是休息提醒部署到cloudflare".

### Details
The conversation was about rest-reminder, but "网站" was ambiguous. I assumed personal-site. The user had to explicitly clarify.

### Suggested Action
When user says "更新网站" in the context of a specific project, confirm which site before deploying. Or default to the project being discussed.

### Metadata
- Source: user_feedback
- Related Files: `rest-reminder-site/`, `personal-site/`
- Tags: deployment, ambiguity, user-correction
- See Also: LRN-20260610-003

---

## [LRN-20260614-001] correction

**Logged**: 2026-06-14T13:30:00+08:00
**Priority**: high
**Status**: pending
**Area**: frontend

### Summary
`_show_goal_dialog` missing `event` parameter causes immediate dialog close on click.

### Details
`_prompt_goal` sets `self.goal_label.mousePressEvent = self._show_goal_dialog`. The mousePressEvent callback receives a `QEvent` argument, but `_show_goal_dialog(self)` didn't accept it → PyQt5 silently swallows the call → dialog never opens. Fix: `def _show_goal_dialog(self, event=None):`.

### Suggested Action
When overriding mousePressEvent with a custom method, always accept an optional `event` parameter.

### Metadata
- Source: user_feedback
- Related Files: `rest_reminder.py`
- Tags: pyqt5, event-handling
- Pattern-Key: event.mousePressEvent_signature

---

## [LRN-20260614-002] best_practice

**Logged**: 2026-06-14T13:30:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
Extract activity detection algorithm from cumulative ratio to idle-growth detection.

### Details
Original `active_ratio = 1 - min(idle / elapsed, 0.8)` was flawed: idle measures total session idle time (from GetTickCount), not per-period idle. When user resumes after 300s idle, the cumulative ratio stays low for minutes even though they're now active, causing phantom detection. Fixed: compare `idle > last_idle` (idle counter growing = user away) vs `idle < last_idle` (idle reset = user active). Simpler, correct.

### Suggested Action
Use delta-based idle detection (compare consecutive `_get_idle_seconds()` calls) instead of cumulative ratio for activity monitoring.

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`
- Tags: activity-detection, algorithm
- Pattern-Key: activity.delta_idle_detection

---

## [LRN-20260614-003] best_practice

**Logged**: 2026-06-14T13:30:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
Copy-paste of `_show_eye_rest_reminder` body into `_show_goal_dialog` caused spurious eye-rest trigger.

### Details
Three orphan lines at end of `_show_goal_dialog`: docstring `"""显示 20-20-20 护眼提醒浮窗"""` + `self.eye_rest_overlay.show_reminder()` + log call. These ran every time the goal dialog closed, spurious triggering the eye-rest overlay. Appeared to be copy-paste accident from `_show_eye_rest_reminder` (which is the very next method). This was caught by /simplify agent's altitude review.

### Suggested Action
After refactoring/adding methods, always review for orphan paste fragments in adjacent methods.

### Metadata
- Source: simplify-and-harden
- Related Files: `rest_reminder.py`
- Tags: code-review, copy-paste
- Pattern-Key: simplify.orphan_paste
- Recurrence-Count: 1
- First-Seen: 2026-06-14
- Last-Seen: 2026-06-14

**Logged**: 2026-06-10T23:55:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Cloudflare Pages deploy: use `wrangler@3 pages deploy`, not `wrangler@2 pages publish` (deprecated). Remove files >25MB before upload.

### Details
- `wrangler@2 pages publish` → deprecated, gives confusing errors
- `wrangler@3 pages deploy . --project-name=xxx` → works
- CF Pages rejects files >25MB (RestReminder.exe was 45MB in out/)
- Environment variable must be exported: `export CLOUDFLARE_API_TOKEN=...` then `wrangler pages deploy`
- Cloudflare API direct upload with multipart is unreliable; wrangler CLI is the way

### Suggested Action
Always use wrangler@3 for CF Pages. Before deploying, check for files >25MB and remove them from out/.

### Metadata
- Source: error
- Related Files: `rest-reminder-site/next.config.ts`
- Tags: cloudflare, wrangler, deploy
- Pattern-Key: deploy.cf_pages_wrangler
- Recurrence-Count: 1
- First-Seen: 2026-06-10
- Last-Seen: 2026-06-10

---

## [LRN-20260618-003] best_practice

**Logged**: 2026-06-18T18:30:00Z
**Priority**: medium
**Status**: resolved
**Area**: docs

### Summary
会话结束时必须记录详细进度，方便后续续接

### Details
本次会话涉及大量修改（看门狗移除、搜索规则、UI卡片化、FloatingBall菜单等），结束后保存了 PROGRESS.md。包含完成状态(10项)、未完成任务(4项)、文件修改清单(22个文件)、技术配置(Clerk/Supabase/GLM/搜索工具)等。

### Metadata
- Source: best_practice
- Related Files: ~/Desktop/休息提醒/PROGRESS.md
- Tags: handoff, progress

---

## [LRN-20260619-001] correction

**Logged**: 2026-06-19T14:00:00Z
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
`self.autostart_action` 从未创建却在 `toggle_autostart()` 中调用 → 每次点托盘自启菜单必崩

### Details
`rest_reminder.py` 的 `toggle_autostart()` 调用 `self.autostart_action.setChecked(new_state)`，但 `autostart_action` 从未被定义。修复：改为调用 `self._toggle_autostart_btn()`。

### Suggested Action
在调用 `self.XXX` 之前，先 grep 确认该属性已定义。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`
- Tags: pyqt5, tray-menu, crash
- Pattern-Key: harden.undefined_attribute

---

## [LRN-20260619-002] correction

**Logged**: 2026-06-19T14:00:00Z
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
`_prompt_goal` 方法体只有 `pass` → 启动时永远不会弹出目标选择对话框

### Details
`_prompt_goal` 在 `init_ui` 中被调用，但方法体只有 `try: pass except: log`。修复：`pass` → `self._show_goal_dialog()`。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`

---

## [LRN-20260619-003] best_practice

**Logged**: 2026-06-19T14:00:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
16 处 `# 已移除UI` 注释代码占用 60+ 行，增加认知负担

### Details
`update_battery_status`、`update_computer_usage` 等方法中有 16 处 `# 已移除UI` 标记的注释代码行。应该直接删除，如果需要参考可以查 git history。

### Suggested Action
在每次 UI 重构时，直接删除被移除的代码而不是注释掉。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`
- Tags: dead-code, cleanup
- Pattern-Key: simplify.commented_out_code

---

## [LRN-20260619-004] insight

**Logged**: 2026-06-19T14:00:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
4 并行 agent 扫描比单 agent 发现更多问题（3 vs 12 个）

### Details
本次会话使用 4 个并行 agent（Reuse/Simplification/Efficiency/Altitude）扫描同一份 diff，总共发现了 12 个问题。Efficiency agent 发现的"重复读"问题是其他 agent 没发现的，因为它关注的是 I/O 模式而非代码结构。

### Suggested Action
对于重要的代码变更，使用 4 个并行 agent 从不同角度扫描。

### Metadata
- Source: conversation
- Tags: code-review, multi-agent

---

## [LRN-20260619-005] correction

**Logged**: 2026-06-19T14:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
`_bilibili_dns_error_logged` 在 `get_bilibili_videos()` 内部重置，每次调用都变为 False

### Details
注释说"DNS 错误只记一次"，但 `self._bilibili_dns_error_logged = False` 在方法开头重置。修复：将初始化移到 `__init__` 中。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`

---

## [LRN-20260619-006] best_practice

**Logged**: 2026-06-19T14:00:00Z
**Priority**: low
**Status**: pending
**Area**: frontend

### Summary
`_load_json` 从 TrendWindow 提取到模块级是正确的跨类共享模式

### Details
这个模式在代码库里已有先例：`_load_goal()`、`_save_goal()` 等都是模块级函数。当发现一个方法被多个类调用时，考虑将其提取到模块级。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`

---

## [LRN-20260619-007] insight

**Logged**: 2026-06-19T14:00:00Z
**Priority**: low
**Status**: pending
**Area**: frontend

### Summary
`update_display()` 每秒执行，但 `datetime.now()` 被调用 3 次

### Details
在 idle 状态下，`update_display()` 调用 `_handle_idle()` 和 `_update_break_display()`，这两个方法各自又调用 `datetime.now()`。可以通过传递 `now` 参数避免。对于每秒执行的热路径方法，避免重复计算相同的值。

### Metadata
- Source: conversation
- Related Files: `rest_reminder.py`

---

---

## [LRN-20260619-008] insight

**Logged**: 2026-06-19T21:00:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
PyInstaller 不会自动打包 `storage.py`——需要显式声明或验证 import 链

### Details
创建了 `storage.py` 并在 `rest_reminder.py` 顶部 `from storage import JSONStore`，但 PyInstaller 打包时没有自动跟踪这个依赖。导致 exe 启动时 `ImportError: No module named 'storage'`，程序崩溃。

需要在 spec 文件中显式添加 `hiddenimports=['storage']` 或用 `--hidden-import storage` 参数。或者每次清理 build/ 目录后重建（`rm -rf build/ && python -m PyInstaller ...`）。

**正确做法**：修改 RestReminder.spec，在 Analysis 中添加 `hiddenimports=['storage']`。

### Suggested Action
修改 RestReminder.spec：
```python
a = Analysis(
    ['rest_reminder.py'],
    ...
    hiddenimports=['storage'],
    ...
)
```

### Metadata
- Source: error
- Related Files: `RestReminder.spec`, `storage.py`

---

## [LRN-20260619-009] insight

**Logged**: 2026-06-19T21:00:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Turbopack 在中文路径下 panic，即使项目路径是英文但文件名含中文字符也会触发

### Details
`D:\rest-reminder-site\` 构建时，Turbopack 内部生成的临时文件名包含中文字符（如 `Desktop_休息提醒_rest-reminder-site__next-internal_...`），导致 `start byte index 19 is not a char boundary` 错误。

即使项目目录本身英文名，只要路径树中任何一级包含中文（如 `Desktop\休息提醒\`），Turbopack 就会 panic。

**解决方案**：将项目复制到纯英文路径（如 `D:\rest-reminder-site\`）再构建。已验证有效。

### Suggested Action
在 CF Pages 部署脚本中，先 `xcopy /E /I rest-reminder-site D:\rest-reminder-site` 再构建。或在 README 中注明此限制。

### Metadata
- Source: error
- Related Files: `experience-cloudflare-pages-complete.md`

---

## [LRN-20260619-010] insight

**Logged**: 2026-06-19T21:00:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
大规模配色重构时，颜色值应先定义为常量再引用

### Details
在 Claude 风格重构中，将金色 `#d4af37` 替换为珊瑚色 `#c9836e` 时，需要在 10+ 处 setStyleSheet 中逐一替换。由于没有集中式颜色常量，容易遗漏或出错。

**建议**：在 `storage.py`（或新建 `theme.py`）中定义颜色常量：
```python
CORAL = (201, 131, 110)
BG_DARK = '#0a0a0b'
BG_CARD = '#141416'
```
然后所有 setStyleSheet 引用这些常量。

### Metadata
- Source: simplify-and-harden
- Related Files: `rest_reminder.py`, `storage.py`

---

## [LRN-20260619-011] insight

**Logged**: 2026-06-19T21:00:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
`frontend-design` skill 仅适用于 Web 前端，不适用于 PyQt5 桌面应用

### Details
当用户要求用 frontend-design 辅助设计时，我错误地拒绝了，理由是"PyQt5 不是 Web"。但实际上用户的官网（`rest-reminder-site`，Next.js + Tailwind）完全可以用 frontend-design。

**正确做法**：
- 网站（Next.js）：使用 frontend-design skill
- 桌面应用（PyQt5）：不使用 frontend-design，直接修改 setStyleSheet

当用户说"全部"时，应该同时处理两个项目。

### Metadata
- Source: user_feedback
- Related Files: `rest-reminder-site/`, `rest_reminder.py`

---

## [LRN-20260619-012] best_practice

**Logged**: 2026-06-19T21:00:00Z
**Priority**: high
**Status**: pending
**Area**: frontend

### Summary
`update_computer_usage_display` 是死方法——计算了变量但从未 setText

### Details
方法 `update_computer_usage_display()` 计算了 `total_h`、`total_m`、`cycle_usage`、`countdown_pct`、`remaining_h`、`remaining_m` 等 6 个变量，但没有调用任何 `setText()` 或 `setValue()` 来更新 UI。

该方法在日期切换时被调用（`self.update_computer_usage_display()`），但实际效果为零。

**教训**：编写 UI 更新方法时，确保每个计算的值都被用于更新某个 widget。如果方法名和实际行为不匹配，要么修正要么删除。

### Metadata
- Source: simplify-and-harden
- Related Files: `rest_reminder.py`

---

## [LRN-20260619-013] insight

**Logged**: 2026-06-19T21:00:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
`_bilibili_dns_error_logged` 标志在方法内设置后永不重置，导致 WARP 恢复后静默失败

### Details
`get_bilibili_videos()` 方法中，当 DNS 错误时设置 `self._bilibili_dns_error_logged = True`，之后所有后续请求都跳过日志记录。但这个标志从未在日期切换或网络恢复时重置。

如果用户从 WARP 切换到正常网络，B站 API 仍然不会尝试请求（因为错误标志已设置），导致永远无法恢复。

**正确做法**：在日期切换时（`update_display()` 中的日期变化检测块）重置该标志。

### Metadata
- Source: simplify-and-harden
- Related Files: `rest_reminder.py`

---


---

## [LRN-20260619-014] best_practice

**Logged**: 2026-06-19T22:00:00Z
**Priority**: low
**Status**: pending
**Area**: docs

### Summary
yao-open-prompts 仓库结构启示：标准 frontmatter + 场景分类 + 引例分离 + 自动化质检

### Details
[yaojingang/yao-open-prompts](https://github.com/yaojingang/yao-open-prompts) 是一个 117 个提示词的开源仓库，值得借鉴的点：
- 统一 YAML frontmatter（title/category/version/status/tags）
- 按使用场景而非技术分类（9 类）
- 描述性文件名（contract-generator.md）
- 英文全镜像到 prompts-en/
- `scripts/check_repo.py` 自动化质量检查

### Metadata
- Source: reading
- Pattern-Key: docs.prompt-library-structure
- See Also: yao-open-prompts

## [LRN-20260620-001] correction

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: frontend

### Summary
`show_stats()` 每次点击都调用 `save_daily_stats()` 覆盖写入，导致报告数据不稳定

### Details
用户每次点击"报告分析"按钮，`show_stats()` 都先调用 `LocalSync.save_daily_stats()` 把内存中的数据写入 `.stats_history.json`，然后再读取同一文件显示在 TrendWindow 中。问题在于：
1. `save_daily_stats()` 写入可能和 TrendWindow 的读取产生竞争
2. 如果用户快速多次点击，文件被反复写入，可能导致 JSON 解析异常
3. `pro_features._load_json()` 读取的是 `rest-reminder-pro/` 目录下的文件（路径不同），导致模块级导入时数据不一致

### Suggested Action
`show_stats()` 不应在每次点击时写入数据。数据应在关键事件（倒计时完成、日期切换、退出）时保存，UI 只负责展示。

### Resolution
- **Resolved**: 2026-06-20T01:30:00Z
- **Notes**: 从 `show_stats()` 中移除了 `LocalSync.save_daily_stats()` 调用

### Metadata
- Source: user_feedback
- Related Files: `rest_reminder.py`
- Tags: data-stability, save-timing
- Pattern-Key: harden.no_redundant_save_on_read

---

## [LRN-20260620-002] correction

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: config

### Summary
`pro_features` 模块路径未加入 `sys.path`，导致 `from pro_features import generate_report` 崩溃

### Details
`rest-reminder-pro/pro_features/__init__.py` 在 `rest-reminder-pro/` 子目录中，但主程序 `rest_reminder.py` 没有把该目录加入 `sys.path`。点击"AI 报告"时 `ModuleNotFoundError: No module named 'pro_features'`，触发 `sys.excepthook` 导致程序退出。

### Suggested Action
在主程序启动时，将 `rest-reminder-pro/` 目录加入 `sys.path`。类似处理 `vendor/` 目录的方式。

### Resolution
- **Resolved**: 2026-06-20T01:30:00Z
- **Notes**: 在 `rest_reminder.py` 顶部添加 `_PRO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest-reminder-pro')` 并 `sys.path.insert(0, _PRO_DIR)`

### Metadata
- Source: error
- Related Files: `rest_reminder.py`, `rest-reminder-pro/pro_features/__init__.py`
- Tags: sys.path, import, pro_features
- Pattern-Key: config.project_subdir_syspath

---

## [LRN-20260620-003] correction

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: frontend

### Summary
`TrendWindow` 设了 `WA_DeleteOnClose`，关闭后 C++ 对象被销毁，但 `_clear_tab` 和 `_refresh_active_tab` 仍操作已销毁的对象导致 RuntimeError

### Details
`TrendWindow` setAttribute(Qt.WA_DeleteOnClose)，用户关闭窗口后 Qt C++ 对象被释放，但 Python 侧的 `self._review_tab` 等引用还在。下次调用 `_refresh_active_tab()` → `_clear_tab()` → `item.widget().setParent(None)` 时触发 `RuntimeError: wrapped C++ object has been deleted`。

### Suggested Action
在 `_clear_tab` 和 `_refresh_active_tab` 中捕获 `RuntimeError`，遇到已销毁的 C++ 对象时静默跳过。

### Resolution
- **Resolved**: 2026-06-20T01:30:00Z
- **Notes**: 在 `_clear_tab` 中 `item.widget().setParent(None)` 外加 try/except RuntimeError；在 `_refresh_active_tab` 中也加了 RuntimeError 捕获

### Metadata
- Source: error
- Related Files: `rest_reminder.py`
- Tags: pyqt5, WA_DeleteOnClose, RuntimeError
- Pattern-Key: harden.wa_delete_on_close_guard

---

## [LRN-20260620-004] insight

**Logged**: 2026-06-20T01:30:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
稳定版冻结工作流：修改在工作版做，稳定版不动

### Details
用户明确要求：修改代码时不能影响自己正在使用的版本。解决方案是冻结一个稳定版副本（`休息提醒_稳定版/`），所有开发修改只在工作版（`休息提醒/`）中进行。用户直接运行稳定版 exe，不受开发修改影响。

工作流：
1. 用户运行稳定版（`休息提醒_稳定版/dist/RestReminder.exe`）
2. 开发者修改工作版（`休息提醒/rest_reminder.py`）
3. 修改后 Python 运行验证
4. 确认无误后重新打包并更新稳定版
5. 更新数据文件到稳定版目录

### Suggested Action
维护两个目录，稳定版只用于运行，工作版用于开发。打包后同步数据文件到稳定版。

### Metadata
- Source: user_feedback
- Related Files: `项目进度.md`, `开发工作流.md`
- Tags: workflow, stable-version, dev-workflow

---

## [LRN-20260620-005] best_practice

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: config

### Summary
子目录中的模块需要显式加入 sys.path，Python 不会自动搜索项目子目录

### Details
`rest-reminder-pro/pro_features/__init__.py` 和 `rest-reminder-pro/backend.py` 都在 `rest-reminder-pro/` 子目录中。即使 `rest_reminder.py` 能 import 顶层模块，子目录中的模块也不会被自动发现。必须在启动时显式将子目录加入 `sys.path`。

同样的问题也出现在 `rest-reminder-site/src/` 中的 Next.js 模块（但由 Node.js 处理，机制不同）。

### Suggested Action
项目中的子目录模块（如 `rest-reminder-pro/`、`rest-reminder-site/`）应在主程序启动时显式加入 sys.path：
```python
_PRO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest-reminder-pro')
if _PRO_DIR not in sys.path:
    sys.path.insert(0, _PRO_DIR)
```

### Metadata
- Source: error
- Related Files: `rest_reminder.py`
- Tags: sys.path, python-imports, project-structure
- Pattern-Key: config.subdir_module_syspath

---

## [LRN-20260620-006] correction

**Logged**: 2026-06-20T02:10:00Z
**Priority**: high
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: frontend

### Summary
`setWindowFlags(Qt.FramelessWindowHint)` 在 `setGeometry()` 之后调用会导致窗口被重置为默认大小（48x48）

### Details
在 `init_ui()` 中，`setGeometry(100, 100, 400, 580)` 在 `setWindowFlags(FramelessWindowHint)` 之前调用。当设置 `FramelessWindowHint` 时，Qt 会重新创建窗口内部句柄，导致之前设置的几何尺寸丢失，窗口变为最小默认大小（48x48）。

**修复**：将 `setWindowFlags()` 移到 `setGeometry()` 之前。

### Suggested Action
在 PyQt5 中，`setWindowFlags()` 必须在 `setGeometry()` 之前调用。如果需要在设置 flags 后调整尺寸，可以再次调用 `setGeometry()` 或 `resize()`。

### Metadata
- Source: error
- Related Files: `rest_reminder.py`
- Tags: pyqt5, window-flags, geometry
- Pattern-Key: harden.setwindowflags_order

---

## [LRN-20260620-007] correction

**Logged**: 2026-06-20T02:10:00Z
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
`setValue()` 传入 float 会导致 TypeError，需要显式 int() 转换

### Details
`QProgressBar.setValue()` 只接受 int 参数。当计算结果为 float 时（如 `max(progress, 0)` 中 progress 是 float），会触发 `TypeError: setValue(self, value: int): argument 1 has unexpected type 'float'`。

**修复**：所有 `setValue()` 调用外层加 `int()` 转换。

### Suggested Action
项目中所有 `setValue()` 调用都应该包裹 `int()`，因为计算链中可能混入 float。

### Metadata
- Source: error
- Related Files: `rest_reminder.py`
- Tags: pyqt5, type-safety, progress-bar

---

## [LRN-20260620-001] best_practice

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
WA_DeleteOnClose 窗口 + QTimer.singleShot 的组合必须有生命周期保护

### Details
- TrendWindow 设置了 Qt.WA_DeleteOnClose（关闭后 C++ 对象销毁）
- showEvent 中发的 QTimer.singleShot(50, callback) 在窗口关闭后仍会触发
- 此时 self.tabs 已变成 None → AttributeError
- 解决方案：_clear_tab 用 sip.isdeleted() 检查，_refresh_active_tab 加 AttributeError catch

### Suggested Action
任何使用 WA_DeleteOnClose 的窗口，其 showEvent 中发出的 delayed callback 必须检查窗口是否还存在

### Metadata
- Source: error
- Related Files: rest_reminder.py:927 (_clear_tab), rest_reminder.py:991 (_refresh_active_tab)
- Pattern-Key: harden.pyqt_lifecycle

---

## [LRN-20260620-002] correction

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
子目录模块导入必须验证实际运行路径，不能只做语法检查

### Details
- 代码有 sys.path.insert(0, _PRO_DIR)，但 Windows Store python 路径下运行时路径解析不同
- pro_features 在 rest-reminder-pro/pro_features/ 中（嵌套两层）
- 只加 rest-reminder-pro/ 到 sys.path 不够，因为 pro_features 还需要 __init__.py
- 实际测试发现需要正确设置路径才能 import 成功

### Suggested Action
- 用绝对路径：os.path.dirname(os.path.abspath(__file__))
- 运行时验证 import 是否成功，不要假设语法检查通过就万事大吉

### Metadata
- Source: error
- Related Files: rest_reminder.py:22-25
- Pattern-Key: harden.module_import

---

## [LRN-20260620-003] best_practice

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
重构设置对话框后必须检查所有按钮引用是否完整

### Details
- _show_settings_dialog 中使用了 save_btn 和 close_btn
- 但重构时遗漏了按钮的 QPushButton 创建代码
- 只有 connect 调用，没有定义 → NameError
- 语法检查无法发现（变量不存在不报语法错，运行时才报）

### Suggested Action
- 重构后 grep 确认所有局部变量都有定义
- 添加对话框时按模板检查：所有按钮是否创建、布局是否添加

### Metadata
- Source: error
- Related Files: rest_reminder.py:_show_settings_dialog
- Pattern-Key: simplify.refactor_completeness

---

## [LRN-20260620-004] correction

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
except Exception: pass 是反模式，必须至少加 log

### Details
- 代码中有 ~12 处 except Exception: pass，导致问题静默消失
- 这些位置包括：单实例锁清理、提示音播放、WindowsApps检测、趋势日期解析等
- 修复后日志显示了真实的错误信息，帮助定位问题

### Suggested Action
- 所有 except 块必须至少加 log.warning 或 log.error
- 唯一可以 pass 的：已知 benign 的 RuntimeError（WA_DeleteOnClose 后）

### Metadata
- Source: user_feedback + error
- Related Files: rest_reminder.py (多处)
- Pattern-Key: harden.error_logging

---

## [LRN-20260620-005] best_practice

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: tests

### Summary
PyQt 应用的回归测试不能只做语法检查，需要实际启动验证

### Details
- py_compile 通过 ≠ 应用能正常运行
- 运行时 crash（NameError, ModuleNotFoundError）在静态检查中不可见
- 需要：清理锁文件 → 启动应用 → 检查 crash.log → 确认进程存活
- 完整验证流程：rm lock → python app → check log → ps check

### Suggested Action
建立 PyQt 应用的快速 smoke test：启动→等3秒→检查进程和日志

### Metadata
- Source: experience
- Related Files: rest_reminder.py
- Pattern-Key: tests.smoke_test_pyqt

---

## [LRN-20260621-001] python_unicode_escapes_in_string_literals

**Logged**: 2026-06-21
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
Python 源码中通过脚本写入 Unicode 字符时，quadruple escape (`\\\\u`) 产生字面量反斜杠而非 Unicode 字符

### Details
`_fix_running2.py` 中写 `\\\\u26a1` 到 .py 文件，实际输出的是 `⚡` 字面量而非 ⚡。Python 的 `\uXXXX` 转义只在源码字符串字面量中由编译器解析，运行时写文件需要直接写 UTF-8 字节。

### Suggested Action
脚本修改 .py 文件时，Unicode 字符直接写在脚本的 Python 字符串字面量中（Python 编译器自动转义），不要用转义序列。

### Metadata
- Source: error
- Related Files: rest_reminder.py
- Tags: python, unicode, code-generation
- Pattern-Key: lang.unicode_escape_in_codegen

---

## [LRN-20260621-002] pyqt_progressbar_int_only

**Logged**: 2026-06-21
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
PyQt5 `QProgressBar.setValue()` 只接受 int，float 操作数的 `//` 地板除返回 float

### Details
`self._remaining * 100 // self._total_seconds` — 当 `_remaining` 是 float（来自 `timedelta.total_seconds()`）时，`//` 返回 float。修复：`int(pct)`。

### Suggested Action
所有 Qt 数值 API 调用前显式 int() 转换。

### Metadata
- Source: error
- Related Files: rest_reminder.py:675
- Tags: pyqt5, type-safety
- Pattern-Key: framework.pyqt_type_safety

---

## [LRN-20260621-003] refactor_script_string_match_fragile

**Logged**: 2026-06-21
**Priority**: high
**Status**: resolved
### Summary
refactor 脚本的字符串匹配替换不生效（空白/缩进差异），导致旧代码残留

### Details
`_refactor_v43.py` 对 `_handle_running` 的替换因为缩进差异未生效。改为按行号切片替换成功。大方法替换优先用行号而非字符串匹配。

### Suggested Action
refactor 脚本改用行号定位或 AST 操作，不要依赖字符串精确匹配。

### Metadata
- Source: error
- Related Files: _refactor_v43.py, rest_reminder.py
- Tags: refactor, automation
- Pattern-Key: dev.refactor_script_robustness

---

## [LRN-20260621-004] state_machine_trio_check

**Logged**: 2026-06-21
**Priority**: high
**Status**: resolved
### Summary
新增状态机状态时必须同步更新三处：`_BTN_CONFIG`、`_handle_*` 方法、主循环路由

### Details
新增 `'resting'` 状态后忘了更新 `_BTN_CONFIG`，导致 KeyError crash。

### Suggested Action
新增状态时检查清单：dict → method → router。

### Metadata
- Source: error
- Related Files: rest_reminder.py
- Tags: state-machine, crash-prevention
- Pattern-Key: arch.state_machine_trio

---
