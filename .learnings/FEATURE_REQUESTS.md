# Feature Requests

Capabilities requested by the user.

---

## [FEAT-20260610-001] eye_rest_pro_configurable_interval

**Logged**: 2026-06-10T23:45:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Requested Capability
Make the 20-20-20 eye rest interval configurable (15/20/25/30 minutes) in Pro version.

### User Context
User experiences eye pain during long study sessions. The 20-minute interval is based on medical consensus, but different users may prefer different intervals. Pro feature candidate.

### Complexity Estimate
simple

### Suggested Implementation
Add `eye_rest_interval` to `user_settings.py` (Pro) with dropdown in settings UI. Free version stays fixed at 20 minutes. Already have `self.eye_rest_interval` in code — just need UI + persistence.

### Metadata
- Frequency: first_time
- Related Features: 20-20-20 eye rest reminder

---
