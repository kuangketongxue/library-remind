"""
休息提醒 Pro — 功能模块
Pro 功能门控 + 高级功能实现

⚠️ 全民限免模式（2026-06-17 ~ 2027-01-01）
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

# 添加当前目录到路径，确保能导入 backend
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from backend import SubscriptionManager, DeviceFingerprint, SupabaseClient, auto_sync

# 限免截止日期
_FREE_TIER_DEADLINE = datetime(2027, 1, 1).date()


# ============================================================
# 订阅状态检查（核心）
# ============================================================

def is_pro(force_refresh=False):
    """
    ⚠️ 全民限免模式 — 2027-01-01 前所有用户都是 Pro
    到期后恢复 SubscriptionManager 云查询
    """
    if datetime.now().date() < _FREE_TIER_DEADLINE:
        return True
    # 限免到期后走正常订阅查询
    device_id = DeviceFingerprint.get_device_id()
    result = SubscriptionManager.check_subscription(device_id)
    return result.get("active", False)


def get_subscription_info():
    """获取订阅详细信息"""
    if datetime.now().date() < _FREE_TIER_DEADLINE:
        return {"active": True, "expires_at": "2027-01-01", "source": "free_tier"}
    device_id = DeviceFingerprint.get_device_id()
    return SubscriptionManager.check_subscription(device_id)


def refresh_subscription():
    """强制刷新订阅状态"""
    if datetime.now().date() < _FREE_TIER_DEADLINE:
        return True
    device_id = DeviceFingerprint.get_device_id()
    result = SubscriptionManager._check_cloud(device_id)
    if result is not None:
        SubscriptionManager._save_cache(result)
        return result.get("active", False)
    cache = SubscriptionManager._check_cache()
    return cache.get("active", False) if cache else False


# ============================================================
# Pro 功能：云同步
# ============================================================

def sync_to_cloud(local_data: dict):
    """同步学习数据到云端（仅Pro）"""
    if not is_pro():
        return False
    return auto_sync(local_data)


def fetch_from_cloud(start_date=None, end_date=None):
    """从云端获取学习数据（仅Pro）"""
    if not is_pro():
        return None
    device_id = DeviceFingerprint.get_device_id()
    client = SupabaseClient()
    result = client.get_study_data(device_id, start_date, end_date)
    if result.get("ok"):
        return result.get("data", [])
    return None


# ============================================================
# Pro 功能：高级统计
# ============================================================

def get_weekly_report(log_dir=None):
    """
    生成周报（仅Pro）
    返回: {"total_study": float, "total_computer": float, "daily": [...]}
    """
    if not is_pro():
        return None

    if log_dir is None:
        log_dir = _parent_dir

    daily_log = os.path.join(log_dir, '.daily_log.json')
    if not os.path.exists(daily_log):
        return None

    try:
        with open(daily_log, 'r', encoding='utf-8') as f:
            all_data = json.load(f)

        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_data = {}

        for date_str, data in all_data.items():
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                if d >= week_start:
                    week_data[date_str] = data
            except ValueError:
                continue

        total_study = sum(d.get("study_hours", 0) for d in week_data.values())
        total_computer = sum(d.get("computer_hours", 0) for d in week_data.values())

        return {
            "total_study": round(total_study, 1),
            "total_computer": round(total_computer, 1),
            "days_active": len(week_data),
            "daily": week_data
        }
    except Exception:
        return None


def get_monthly_report(log_dir=None):
    """生成月报（仅Pro）"""
    if not is_pro():
        return None

    if log_dir is None:
        log_dir = _parent_dir

    daily_log = os.path.join(log_dir, '.daily_log.json')
    if not os.path.exists(daily_log):
        return None

    try:
        with open(daily_log, 'r', encoding='utf-8') as f:
            all_data = json.load(f)

        today = datetime.now()
        month_start = today.replace(day=1)
        month_data = {}

        for date_str, data in all_data.items():
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                if d >= month_start:
                    month_data[date_str] = data
            except ValueError:
                continue

        total_study = sum(d.get("study_hours", 0) for d in month_data.values())
        total_computer = sum(d.get("computer_hours", 0) for d in month_data.values())

        return {
            "total_study": round(total_study, 1),
            "total_computer": round(total_computer, 1),
            "days_active": len(month_data),
            "daily": month_data
        }
    except Exception:
        return None


# ============================================================
# Pro 功能：自定义提醒间隔
# ============================================================

PRO_INTERVALS = [15, 20, 25, 30, 45, 60, 90, 120]  # 分钟

def get_custom_intervals():
    """获取可用的提醒间隔（仅Pro）"""
    if not is_pro():
        return [60]  # 免费版固定60分钟
    return PRO_INTERVALS


# ============================================================
# Pro 功能：数据导出
# ============================================================

def export_to_csv(log_dir=None, output_path=None):
    """导出学习数据为 CSV（仅Pro）"""
    if not is_pro():
        return None

    if log_dir is None:
        log_dir = _parent_dir

    daily_log = os.path.join(log_dir, '.daily_log.json')
    if not os.path.exists(daily_log):
        return None

    try:
        with open(daily_log, 'r', encoding='utf-8') as f:
            all_data = json.load(f)

        if output_path is None:
            output_path = os.path.join(log_dir, f'study_export_{datetime.now().strftime("%Y%m%d")}.csv')

        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write("日期,学习时长(h),电脑时长(h),休息时长(min)\n")
            for date_str in sorted(all_data.keys()):
                d = all_data[date_str]
                f.write(f"{date_str},{d.get('study_hours',0)},{d.get('computer_hours',0)},{d.get('break_minutes',0)}\n")

        return output_path
    except Exception:
        return None


# ============================================================
# Pro 功能：主题
# ============================================================

PRO_THEMES = {
    "default": {"name": "暗黑奢华", "colors": {"bg": "#1a1a2e", "accent": "#e94560", "text": "#eee"}},
    "green": {"name": "护眼绿", "colors": {"bg": "#1a2e1a", "accent": "#4caf50", "text": "#eee"}},
    "minimal": {"name": "极简白", "colors": {"bg": "#f5f5f5", "accent": "#333", "text": "#222"}},
    "ocean": {"name": "深海蓝", "colors": {"bg": "#0a1628", "accent": "#00bcd4", "text": "#eee"}},
}

def get_available_themes():
    """获取可用主题（仅Pro）"""
    if not is_pro():
        return {"default": PRO_THEMES["default"]}
    return PRO_THEMES
