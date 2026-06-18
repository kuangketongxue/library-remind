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
