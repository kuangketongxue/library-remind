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

## [FEAT-20260620-001] remove_pro_subscription_verification

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: resolved
**Area**: frontend

### Requested Capability
移除 Pro/普通用户区分，去掉 Clerk/Supabase/设备验证等所有付费墙逻辑

### User Context
用户认为当前的 Pro 验证逻辑（Supabase 订阅检查、设备指纹、Clerk 认证）把代码搞乱了。用户希望：
1. 先做好基础功能，让所有人都能用
2. AI 报告等功能直接可用，不需要订阅
3. 以后想收费时再单独加，不要预先把代码复杂化
4. 用户需求 > 其他人的需求

当前状态：`pro_features/__init__.py` 中 `is_pro()` 已改为始终返回 True，`generate_report()` 已去掉 `is_pro()` 检查，设置对话框中的设备 ID 和 Pro 登录按钮已删除。

### Complexity Estimate
simple

### Suggested Implementation
已完成。以后收费时再添加：
1. `is_pro()` 改为读取本地许可证文件或调用 API
2. 在设置中添加"激活 Pro"入口
3. 未激活用户限制部分功能（或显示广告/水印）

### Metadata
- Frequency: first_time
- Related Features: AI 报告、Pro 版功能

---

## [FEAT-20260620-002] fixed_bilibili_favlist_url_for_break

**Logged**: 2026-06-20T01:30:00Z
**Priority**: high
**Status**: pending
**Area**: frontend

### Requested Capability
休息时自动打开固定的 B 站收藏夹链接（不需要随机选择视频）

### User Context
当前休息逻辑是随机打开 B 站收藏夹中的一个视频。用户希望：
1. 休息 5 分钟后自动打开固定链接：`https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create`
2. 提示休息结束了
3. 每 1 小时休息 5 分钟（不变）
4. 每 3 小时的提醒不变

### Complexity Estimate
simple

### Suggested Implementation
修改休息流程：
1. 1 小时到 → 提示音（已有）→ 5 分钟倒计时浮层（已有）
2. 5 分钟到 → 打开固定 B 站链接（替代随机视频）→ 提示"休息结束"
3. 用户手动点击开始下一个小时（不自动重启）

需要修改的位置：
- `_handle_running()` 中 `remaining <= 0` 的分支
- 去掉 `open_random_video()` 调用
- 改为 `open_url("https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create")`

### Metadata
- Frequency: first_time
- Related Features: B 站收藏夹播放、休息提醒

---
