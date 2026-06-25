# 休息提醒 v4.3 — 待办清单（已完成）

> 2026-06-22 建立。规格见 产品规格-v4.3.md
> 2026-06-25 全部完成，归档。

---

## 全部完成 ✅

### 1. 复盘评分升级：1-5⭐ → 1-100分 + 学科 + 标签
- `_prompt_review()` → `_build_review_dialog()` 重建弹窗 UI
- `.review_log.json` schema：`{time, subject, label, score, round_goal}`
- 自动提交 30秒，补录 `_catchup_review()` 同步升级

### 2. 22:00 强制结束 + 填写窗口
- `_update_countdown()` → 强制 idle + 弹出"今日完成"窗口
- `_day_ended` flag → `on_start_clicked()` 检查
- `.daily_log.json` 写入 `daily_summary`

### 3. 每日目标升级：下拉 → 自由文本 + 预计轮次
- `_show_goal_dialog()` → 自定义 QDialog（自由文本 + 数字输入）
- `.daily_log.json` 写入 `daily_goal: {description, planned_rounds}`
- 每天首次点击"开始学习"时触发

### 4. 每轮目标弹窗（新功能）
- 休息结束后弹轻量窗口 → 6学科按钮 + 单行输入
- 3秒自动提交 → 写入 `.review_log.json` round_goal/subject

### 5. `.review_log.json` Schema 扩展
- 新格式：`{time, subject, label, score, round_goal}`
- 旧数据兼容：缺省字段 → "未记录"

### 6. `.daily_log.json` Schema 扩展
- 新增 `daily_goal` + `daily_summary` 字段

### 7. B站链接规则（已确认，不改代码）
- `_round_count % 3 == 0` 第 3/6/9... 轮开护眼视频

---

## 不动的（已确认不需要）
- ~~电脑使用3小时提醒~~
- ~~活动密度感知/空闲自动暂停~~
- ~~随机视频~~
- ~~打卡卡片~~
- ~~Pro订阅/收费~~
- ~~20-20-20浮窗~~（已有完整实现）
