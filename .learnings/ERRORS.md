# Errors

Command failures and integration errors.

---

## [ERR-20260610-001] github_push_403

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
GitHub PAT embedded in git remote URL is expired, push returns 403.

### Error
```
remote: Permission to kuangketongxue/library-remind.git denied to kuangketongxue.
fatal: unable to access 'https://github.com/kuangketongxue/...': The requested URL returned error: 403
```

### Context
- Command: `git push origin main`
- Remote URL contains PAT: `github_pat_11BS3DN4Y...`
- `gh auth status` confirms token is invalid
- Need: `gh auth refresh -h github.com` to re-authenticate

### Suggested Fix
Run `gh auth refresh -h github.com` in terminal, then update remote URL with new token.

### Metadata
- Reproducible: yes
- Related Files: `.git/config`
- See Also: ERR-20260610-002

---

## [ERR-20260610-002] netlify_deploy_blocked

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Netlify account credits exceeded, new deploys blocked.

### Error
```
{"error":"Account credit usage exceeded - new deploys are blocked until credits are added"}
```

### Context
- Command: `curl -X POST .../deploys` with zip payload
- Netlify site: `rest-reminder-app` (fb7da69a)
- Auth token works (API returns site info), but deploy endpoint rejects
- Build output (`out/`) is ready, just can't upload

### Suggested Fix
Add credits in Netlify dashboard or wait for free tier refresh. Deploy manually via dashboard if needed.

### Metadata
- Reproducible: yes
- Related Files: `rest-reminder-site/netlify.toml`

---

## [ERR-20260610-003] turbopack_chinese_path

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
Next.js 16 Turbopack build fails when project path contains Chinese characters (休息提醒).

### Error
```
TurbopackInternalError: start byte index 19 is not a char boundary; it is inside '醒' (bytes 17..20)
```

### Context
- Command: `npx next build` in `~/Desktop/休息提醒/rest-reminder-site/`
- Next.js 16.2.7 uses Turbopack by default for builds
- Workaround: copy project to `C:\tmp\rr-build\` (ASCII path), build there, copy `out/` back

### Suggested Fix
Long-term: add `--no-turbopack` flag or configure webpack in next.config.ts. Short-term: build from ASCII path.

### Resolution
- **Resolved**: 2026-06-10T23:40:00+08:00
- **Notes**: Copied to C:\tmp\rr-build, built successfully, copied out/ back

### Metadata
- Reproducible: yes
- Related Files: `rest-reminder-site/next.config.ts`
- Tags: turbopack, chinese-path, nextjs-16

---

## [ERR-20260610-004] wrangler_pages_deploy

**Logged**: 2026-06-10T23:55:00+08:00
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
wrangler@2 `pages deploy` doesn't exist (uses `pages publish` which is deprecated). wrangler@3 requires exported env var. CF Pages rejects files >25MB.

### Error
```
# wrangler@2:
X [ERROR] 'wrangler pages <command>' is a beta command.
# wrangler@3 without export:
X [ERROR] Unable to authenticate request [code: 10001]
# wrangler@3 with large file:
X [ERROR] Pages only supports files up to 25 MiB in size — RestReminder.exe is 45.3 MiB
```

### Context
- `npx wrangler@2 pages deploy` → command doesn't exist
- `CLOUDFLARE_API_TOKEN=xxx wrangler pages deploy` → auth fails (variable not exported)
- `export CLOUDFLARE_API_TOKEN=xxx && wrangler pages deploy` → works, but fails on >25MB files
- `out/` directory had RestReminder.exe (45MB) — removed, then deploy succeeded

### Suggested Fix
1. Always `export` the token, don't inline
2. Remove files >25MB from `out/` before deploying
3. Use wrangler@3: `npx wrangler@3 pages deploy . --project-name=xxx`

### Resolution
- **Resolved**: 2026-06-10T23:55:00+08:00
- **Notes**: Removed exe, used exported env var, wrangler@3 deployed successfully

### Metadata
- Reproducible: yes
- Related Files: `rest-reminder-site/netlify.toml`
- Tags: cloudflare, wrangler, deploy, env-var
- See Also: ERR-20260610-002

---

## [ERR-20260614-001] pyqt5_QFrame_not_imported

**Logged**: 2026-06-14T13:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
Adding `QFrame` usage to `init_ui()` but forgot to add `QFrame` to module-level import from `PyQt5.QtWidgets`.

### Error
```
NameError: name 'QFrame' is not defined
  File "rest_reminder.py", line 1197, in init_ui
    card1 = QFrame()
```

### Context
- Added card-based 2×2 grid layout using `QFrame` widgets
- Import line already had many QtWidgets but missed `QFrame`
- Launch from bash hid the crash; launch from foreground PowerShell uncovered it

### Suggested Fix
Always add new imported classes to the top-level `from PyQt5.QtWidgets import (...)` block immediately when writing the code that uses them.

### Resolution
- **Resolved**: 2026-06-14T13:35:00+08:00
- **Notes**: Added `QFrame` to the import line; crash.log triage identified the error

### Metadata
- Reproducible: yes
- Related Files: `rest_reminder.py`
- See Also: LRN-20260614-001

---

---

## [ERR-20260619-001] PyInstaller_missing_storage_module

**Logged**: 2026-06-19T20:50:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
PyInstaller 打包的 exe 启动崩溃：`ImportError: No module named 'storage'`

### Error
```
Traceback (most recent call last):
  File "rest_reminder.py", line 31, in <module>
    from storage import JSONStore
ModuleNotFoundError: No module named 'storage'
```

### Context
- 创建了 `storage.py` 并在 `rest_reminder.py` 顶部 import
- PyInstaller 没有自动跟踪 `storage.py` 作为依赖
- exe 启动时崩溃

### Suggested Fix
在 RestReminder.spec 的 Analysis 中添加 `hiddenimports=['storage']`

### Resolution
- **Resolved**: 2026-06-19T20:55:00Z
- **Notes**: 通过清理 build/ 目录后重建解决（`rm -rf build/ && python -m PyInstaller ...`）。根本修复需要修改 spec 文件。

---

## [ERR-20260619-002] Turbopack_chinese_path_panic

**Logged**: 2026-06-19T20:50:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
Next.js 16 Turbopack 在中文路径下 panic

### Error
```
Error [TurbopackInternalError]: start byte index 19 is not a char boundary; it is inside '醒' (bytes 17..20) of `Desktop_休息提醒_rest-reminder-site__next-internal_server_app_favicon_ico_route_actions_08b8f2s`
```

### Context
- 项目路径 `C:\Users\binlo\Desktop\休息提醒\rest-reminder-site\` 包含中文
- Turbopack 内部生成的临时文件名包含中文字符
- 导致构建失败

### Suggested Fix
将项目复制到纯英文路径（如 `D:\rest-reminder-site\`）再构建

### Resolution
- **Resolved**: 2026-06-19T20:55:00Z
- **Notes**: 复制到 `D:\rest-remindrome-site\` 后构建成功。已部署到 CF Pages。

---


## [ERR-20260620-001] pro_features_not_in_syspath

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
`ModuleNotFoundError: No module named 'pro_features'` — AI 报告功能崩溃

### Error
```
Traceback (most recent call last):
  File "C:\Users\binlo\Desktop\休息提醒\rest_reminder.py", line 2711, in _show_ai_report
    from pro_features import generate_report
ModuleNotFoundError: No module named 'pro_features'
```

### Context
- 点击"🤖 AI 报告"按钮触发
- `pro_features` 模块在 `rest-reminder-pro/` 子目录中
- `rest_reminder.py` 没有把该目录加入 `sys.path`
- 触发 `sys.excepthook` → `crash.log` 记录 → 程序退出

### Suggested Fix
在主程序启动时将 `rest-reminder-pro/` 目录加入 `sys.path`

### Resolution
- **Resolved**: 2026-06-20T01:30:00Z
- **Notes**: 在 `rest_reminder.py` 顶部添加 sys.path 插入代码

### Metadata
- Reproducible: yes
- Related Files: `rest_reminder.py`, `rest-reminder-pro/pro_features/__init__.py`
- See Also: LRN-20260620-002

---

## [ERR-20260620-002] trendwindow_runtimeerror_on_tab_refresh

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
`TrendWindow` 关闭后刷新标签页触发 `RuntimeError: wrapped C++ object has been deleted`

### Error
```
AttributeError: 'NoneType' object has no attribute 'deleteLater'
```
（实际上是 RuntimeError 被捕获前的表现）

### Context
- `TrendWindow` 设了 `Qt.WA_DeleteOnClose`
- 用户关闭窗口后 C++ 对象被销毁
- `showEvent` → `_refresh_active_tab` → `_clear_tab` → `item.widget().setParent(None)` 操作已销毁的 C++ 对象

### Suggested Fix
在 `_clear_tab` 和 `_refresh_active_tab` 中捕获 `RuntimeError`

### Resolution
- **Resolved**: 2026-06-20T01:30:00Z
- **Notes**: 两处都加了 try/except RuntimeError: pass

### Metadata
- Reproducible: yes
- Related Files: `rest_reminder.py`
- See Also: LRN-20260620-003

---

## [ERR-20260620-001] TrendWindow_clear_tab_AttributeError

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
TrendWindow._clear_tab 反复报错：'NoneType' object has no attribute 'deleteLater'

### Error
```
[TrendWindow] 刷新标签页失败: AttributeError: 'NoneType' object has no attribute 'deleteLater'
```

### Context
- QTimer.singleShot(50, self._refresh_active_tab) 在 showEvent 中触发
- 用户关闭窗口后（WA_DeleteOnClose），C++ 对象已销毁
- singleShot 仍然触发，self.tabs 变成 None
- 原本只 catch RuntimeError，漏了 AttributeError

### Suggested Fix
- _refresh_active_tab 加 `except AttributeError: pass`
- _clear_tab 加 `sip.isdeleted(tab)` 和 `sip.isdeleted(w)` 检查

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:1012 (_clear_tab), rest_reminder.py:991 (_refresh_active_tab)
- See Also: ERR-20260620-002

---

## [ERR-20260620-002] NameError_save_btn_settings_dialog

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
_show_settings_dialog 中 save_btn 和 close_btn 未定义就使用

### Error
```
NameError: name 'save_btn' is not defined
```

### Context
- _show_settings_dialog 中调用了 save_btn.clicked.connect(save_settings)
- 但按钮定义被之前的编辑遗漏了
- crash.log 确认触发位置：line 2723 (旧行号)

### Suggested Fix
在 _show_settings_dialog 中添加 save_btn 和 close_btn 的 QPushButton 创建代码

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:_show_settings_dialog

---

## [ERR-20260620-003] ModuleNotFoundError_pro_features

**Logged**: 2026-06-20T22:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
_show_ai_report 中 from pro_features import generate_report 失败

### Error
```
ModuleNotFoundError: No module named 'pro_features'
```

### Context
- pro_features 在 rest-reminder-pro/ 子目录中
- 代码开头有 sys.path.insert(0, _PRO_DIR)，但 Windows Store python 路径下有时不生效
- crash.log 确认触发位置：line 2711

### Suggested Fix
确保 _PRO_DIR 在 sys.path 中，或在 import 时显式添加路径

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:23-25 (sys.path setup), rest_reminder.py:2751 (import)

---

## [ERR-20260620-005] NameError_hashlib_settings_dialog

**Logged**: 2026-06-20T23:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
点击设置按钮 → 整个应用崩溃退出：`NameError: name 'hashlib' is not defined`

### Error
```
NameError: name 'hashlib' is not defined. Did you forget to import 'hashlib'?
  File "rest_reminder.py", line 2686, in _show_settings_dialog
    dev_id = hashlib.md5(f"{platform.node()}-{uuid.getnode()}".encode()).hexdigest()[:12]
```

### Context
- 用户点击 ⚙️ 设置按钮 → 调用 `_show_settings_dialog()`
- 方法体中用了 `hashlib.md5()`、`uuid.getnode()`、`platform.node()` 生成设备 ID
- 这三个模块在文件顶部没有 import
- 未捕获的 NameError 触发 `sys.excepthook` → crash.log 记录 → 进程退出
- 用户感知：点击设置 → 整个休息提醒关闭

### Suggested Fix
在文件顶部添加 `import hashlib`、`import uuid`、`import platform`

### Resolution
- **Resolved**: 2026-06-20T23:30:00+08:00
- **Notes**: 添加了三个缺失的 import，语法检查通过

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py
- Tags: missing-import, crash, settings-dialog

---

## [ERR-20260620-006] Pro_gate_not_fully_removed

**Logged**: 2026-06-20T23:40:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
已取消 Pro 区分，但 `_show_ai_report` 中仍有 Pro 拦截逻辑，点击 AI 报告仍弹出 Pro 提示

### Error
用户反馈："明明已经取消了pro的区分，为什么点击AI报告会弹出要pro才行"

### Context
- `is_pro()` 已改为始终返回 True
- 但 `_show_ai_report` 中仍有完整 Pro 拦截流程：
  1. `HAS_PRO` 标志检查（import 失败时弹"Pro 版功能"提示）
  2. `if not is_pro()` 分支（显示设备 ID + "需要 Pro 订阅"）
  3. `not_pro` 错误分支（报告视图显示"Pro 订阅验证失败"）
  4. 设置对话框中"打开 Pro 登录界面"按钮
- 只改了 `is_pro()` 的返回值，没改调用方的逻辑分支

### Suggested Fix
完全移除 `_show_ai_report` 中的 Pro 拦截逻辑，直接显示报告类型选择器

### Resolution
- **Resolved**: 2026-06-20T23:40:00+08:00
- **Notes**: 移除了 HAS_PRO 检查、is_pro() 验证、设备 ID 绑定提示、not_pro 错误分支。设置对话框中按钮文字改为"打开官网"。

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:_show_ai_report
- See Also: ERR-20260620-003

---

## [ERR-20260621-001] show_stats_overwrite_data

**Logged**: 2026-06-21T00:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
`show_stats()` 每次调用都执行 `LocalSync.save_daily_stats()`，导致用户多次点击趋势分析按钮时数据被覆盖/丢失

### Error
用户反馈："多次点击数据分析里面的按钮数据就消失了"

### Context
- `show_stats()` 方法中调用了 `LocalSync.save_daily_stats()`，该方法读取当前内存中的 `LocalSync._data` 并覆盖写入 `.daily_log.json`
- 但 `LocalSync._data` 可能在某些时序下包含不完整或过期的数据
- 每次点击趋势按钮都会触发一次写入，多点击后数据"消失"
- 数据实际应该只在关键事件（倒计时结束、日期变更、退出）时保存

### Suggested Fix
从 `show_stats()` 中移除 `LocalSync.save_daily_stats()` 调用，数据保存只在事件驱动时执行

### Resolution
- **Resolved**: 2026-06-21T00:30:00+08:00
- **Notes**: 删除了 `show_stats()` 中的 `LocalSync.save_daily_stats()` 调用

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:show_stats
- See Also: ERR-20260620-002 (TrendWindow 相关问题)

---

## [ERR-20260621-002] settings_double_write

**Logged**: 2026-06-21T00:45:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
设置对话框中 `save_settings()` 和 `_set_reminder_mode()` 同时调用 `LocalSync.save_settings()`，导致双重写入

### Error
用户在设置中切换提醒方式时，同一份设置被写入两次

### Context
- `_set_reminder_mode()`（独立方法）调用 `LocalSync.save_settings(self.app_settings)`
- 设置对话框中 `save_settings()` 也调用 `LocalSync.save_settings(self.app_settings)`
- 提醒方式下拉框的 `currentIndexChanged` 信号之前可能绑定了 `_set_reminder_mode`
- 加上对话框保存时的写入 = 两次写入

### Suggested Fix
移除 `save_settings()` 中的冗余 `LocalSync.save_settings()` 调用

### Resolution
- **Resolved**: 2026-06-21T00:45:00+08:00
- **Notes**: 删除 `save_settings()` 中的 `LocalSync.save_settings()`，由 `_set_reminder_mode` 单独处理

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:_show_settings_dialog, _set_reminder_mode

---

## [ERR-20260621-003] ui_refactor_orphan_references

**Logged**: 2026-06-21T01:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
重构 `init_ui()` 为大面板布局后，`update_study_display`、`_update_break_display`、`_update_streak_display` 仍引用旧卡片 widget（`study_progress_label`、`break_label`、`streak_label`），导致 AttributeError 崩溃

### Error
```
AttributeError: 'RestReminderWidget' object has no attribute 'study_progress_label'
```

### Context
- `init_ui()` 从 2×2 卡片网格改为纵向列表布局（参考 ccswitch 风格）
- 删除了 `study_progress_label`、`study_sub_label`、`study_progress_bar`、`break_label`、`streak_label` 等卡片 widget
- 但三个更新方法仍引用这些 widget → 启动时崩溃
- Edit 工具的 new_string 被截断导致部分代码未正确替换

### Suggested Fix
重写三个更新方法适配新 UI：`update_study_display` → 只更新 `computer_label`；`_update_break_display` → no-op（休息时长在 timer_label 中实时显示）；`_update_streak_display` → no-op（打卡数据后台追踪）

### Resolution
- **Resolved**: 2026-06-21T01:05:00+08:00
- **Notes**: 通过 Python 脚本批量替换三个方法体。注意：大段代码替换用 Edit 工具时 new_string 可能被截断，改用 Python 脚本更可靠

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:init_ui, update_study_display, _update_break_display, _update_streak_display
- See Also: ERR-20260621-001, ERR-20260621-002

---

## [ERR-20260621-004] progressbar_setvalue_float_type_error

**Logged**: 2026-06-21
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
`QProgressBar.setValue()` 传入 float 导致 TypeError crash

### Error
```
TypeError: setValue(self, value: int): argument 1 has unexpected type 'float'
```

### Context
- `CountdownOverlay._update_display()` 中 `self.progress_bar.setValue(max(pct, 0))`
- `pct = self._remaining * 100 // self._total_seconds` — `_remaining` 是 float，`//` 返回 float
- 运行时 crash，非语法错误，py_compile 无法检测

### Suggested Fix
`max(int(pct), 0)` 显式转换

### Resolution
- **Resolved**: 2026-06-21
- **Notes**: 在 setValue 前加 int() 转换

### Metadata
- Reproducible: yes
- Related Files: rest_reminder.py:675
- Tags: pyqt5, type-error

---

## [ERR-20260621-005] refactor_script_string_match_failure

**Logged**: 2026-06-21
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
`_refactor_v43.py` 字符串匹配替换 `_handle_running` 方法体未生效，旧的活动密度感知代码残留

### Error
`_handle_running` 方法体内仍有 `_idle_check_tick`、`_idle_seconds_cached`、`_activity_interval = 45` 等旧代码

### Context
- refactor 脚本用 `old.replace(new)` 替换 87 行方法体
- 缩进差异（tab vs 空格）导致字符串不匹配
- 只有方法签名和局部参数被替换，主体代码残留

### Suggested Fix
改用行号切片替换（`lines[start:end] = [new_content]`），或 AST 操作

### Resolution
- **Resolved**: 2026-06-21
- **Notes**: 创建 `_fix_running2.py` 按行号切片替换成功。同时发现 Unicode 转义问题（见 LRN-20260621-001）

### Metadata
- Reproducible: yes
- Related Files: _refactor_v43.py, rest_reminder.py:2052
- Tags: refactor, automation, reliability

---

---
