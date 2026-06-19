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
