from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
import subprocess
import sys
import threading
import time
import tempfile
import tkinter as tk
import webbrowser
import winreg
import winsound
from dataclasses import dataclass
from pathlib import Path
from ctypes import wintypes


VIDEO_URL = "https://www.bilibili.com/video/BV14Y4y1N7PW/?share_source=copy_web&vd_source=627fcf9c6d3a74e287f35fe190e5fe39"
MUTEX_NAME = "Global\\BreakReminderWidgetSingleton"
ERROR_ALREADY_EXISTS = 183
REMINDER_WINDOW_TITLE = "休息提醒"
WIDGET_HEADER = "休息提醒挂件"
CHECK_INTERVAL_MS = 1000
SPI_GETWORKAREA = 0x0030
COINIT_MULTITHREADED = 0
CLSCTX_ALL = 23
DEVICE_STATE_ACTIVE = 1
eRender = 0
eCapture = 1
eConsole = 0
STGM_READ = 0
VT_LPWSTR = 31
WM_APP = 0x8000
WM_TRAYICON = WM_APP + 1
WM_CREATE = 0x0001
WM_DESTROY = 0x0002
WM_NCCREATE = 0x0081
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205
WM_LBUTTONDBLCLK = 0x0203
NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIM_SETVERSION = 4
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NOTIFYICON_VERSION_4 = 4
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x0010
LR_DEFAULTSIZE = 0x0040
IDI_APPLICATION = 32512
AUDIO_BASELINE_FILE = Path(__file__).with_name("audio_device_baseline.json")


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_size_t),
        ("time", ctypes.c_ulong),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uTimeoutOrVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", ctypes.c_byte * 16),
        ("hBalloonIcon", wintypes.HICON),
    ]


class NOTIFYICONIDENTIFIER(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("guidItem", ctypes.c_byte * 16),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    @classmethod
    def from_string(cls, value: str) -> "GUID":
        guid = cls()
        ctypes.windll.ole32.CLSIDFromString(ctypes.c_wchar_p(value), ctypes.byref(guid))
        return guid


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID), ("pid", wintypes.DWORD)]


class PROPVARIANT(ctypes.Structure):
    _fields_ = [
        ("vt", wintypes.USHORT),
        ("wReserved1", wintypes.USHORT),
        ("wReserved2", wintypes.USHORT),
        ("wReserved3", wintypes.USHORT),
        ("_data", ctypes.c_byte * 16),
    ]


CLSID_MMDeviceEnumerator = GUID.from_string("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = GUID.from_string("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IMMDevice = GUID.from_string("{D666063F-1587-4E43-81F1-B948E807363F}")
IID_IPropertyStore = GUID.from_string("{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}")
IID_IAudioClient = GUID.from_string("{1CB9AD4C-DBFA-4C32-B178-C2F568A703B2}")
IID_IAudioEndpointVolume = GUID.from_string("{5CDF2C82-841E-4546-9722-0CF74078229A}")
FMTID_Device = GUID.from_string("{A45C254E-DF1C-4EFD-8020-67D146A850E0}")
PKEY_Device_FriendlyName = PROPERTYKEY(FMTID_Device, 14)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_uint),
        ("BatteryFullLifeTime", ctypes.c_uint),
    ]


class SYSTEM_BATTERY_STATE(ctypes.Structure):
    _fields_ = [
        ("AcOnLine", ctypes.c_byte),
        ("BatteryPresent", ctypes.c_byte),
        ("Charging", ctypes.c_byte),
        ("Discharging", ctypes.c_byte),
        ("Spare1", ctypes.c_byte * 4),
        ("Tag", ctypes.c_byte),
        ("MaxCapacity", ctypes.c_uint),
        ("RemainingCapacity", ctypes.c_uint),
        ("Rate", ctypes.c_uint),
        ("EstimatedTime", ctypes.c_uint),
        ("DefaultAlert1", ctypes.c_uint),
        ("DefaultAlert2", ctypes.c_uint),
    ]


def _com_method(instance, index: int, restype, *argtypes):
    vtbl = ctypes.cast(instance, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(vtbl[index])


def _co_initialize_audio() -> bool:
    hr = ctypes.windll.ole32.CoInitializeEx(None, COINIT_MULTITHREADED)
    return hr in (0, 1)


def _co_uninitialize_audio(initialized: bool) -> None:
    if initialized:
        ctypes.windll.ole32.CoUninitialize()


def _device_state_to_text(state: int) -> str:
    if state == DEVICE_STATE_ACTIVE:
        return "可用"
    return "不可用"


def _propvariant_to_string(propvariant: PROPVARIANT) -> str:
    if propvariant.vt != VT_LPWSTR:
        return ""
    ptr = ctypes.cast(ctypes.byref(propvariant, 8), ctypes.POINTER(ctypes.c_void_p)).contents.value
    if not ptr:
        return ""
    return ctypes.wstring_at(ptr)


def _read_endpoint_friendly_name(device_ptr) -> str:
    store_ptr = ctypes.c_void_p()
    open_store = _com_method(device_ptr, 4, ctypes.c_long, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p))
    hr = open_store(device_ptr, STGM_READ, ctypes.byref(store_ptr))
    if hr != 0 or not store_ptr.value:
        return ""

    propvariant = PROPVARIANT()
    get_value = _com_method(store_ptr, 5, ctypes.c_long, ctypes.POINTER(PROPERTYKEY), ctypes.POINTER(PROPVARIANT))
    hr = get_value(store_ptr, ctypes.byref(PKEY_Device_FriendlyName), ctypes.byref(propvariant))
    name = _propvariant_to_string(propvariant) if hr == 0 else ""

    try:
        ctypes.windll.ole32.PropVariantClear(ctypes.byref(propvariant))
    except Exception:
        pass

    release = _com_method(store_ptr, 2, ctypes.c_ulong)
    release(store_ptr)
    return name


def _read_endpoint_mute_and_volume(device_ptr) -> tuple[bool | None, float | None]:
    volume_ptr = ctypes.c_void_p()
    activate = _com_method(device_ptr, 3, ctypes.c_long, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    hr = activate(device_ptr, ctypes.byref(IID_IAudioEndpointVolume), CLSCTX_ALL, None, ctypes.byref(volume_ptr))
    if hr != 0 or not volume_ptr.value:
        return None, None

    try:
        mute = wintypes.BOOL()
        get_mute = _com_method(volume_ptr, 14, ctypes.c_long, ctypes.POINTER(wintypes.BOOL))
        hr_mute = get_mute(volume_ptr, ctypes.byref(mute))

        level = ctypes.c_float()
        get_level = _com_method(volume_ptr, 9, ctypes.c_long, ctypes.POINTER(ctypes.c_float))
        hr_level = get_level(volume_ptr, ctypes.byref(level))

        mute_value = bool(mute.value) if hr_mute == 0 else None
        level_value = float(level.value) if hr_level == 0 else None
        return mute_value, level_value
    finally:
        release = _com_method(volume_ptr, 2, ctypes.c_ulong)
        release(volume_ptr)


def _check_mix_format(device_ptr) -> bool:
    client_ptr = ctypes.c_void_p()
    activate = _com_method(device_ptr, 3, ctypes.c_long, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    hr = activate(device_ptr, ctypes.byref(IID_IAudioClient), CLSCTX_ALL, None, ctypes.byref(client_ptr))
    if hr != 0 or not client_ptr.value:
        return False

    mix_format_ptr = ctypes.c_void_p()
    try:
        get_mix_format = _com_method(client_ptr, 3, ctypes.c_long, ctypes.POINTER(ctypes.c_void_p))
        hr_mix = get_mix_format(client_ptr, ctypes.byref(mix_format_ptr))
        return hr_mix == 0 and bool(mix_format_ptr.value)
    finally:
        if mix_format_ptr.value:
            ctypes.windll.ole32.CoTaskMemFree(mix_format_ptr)
        release = _com_method(client_ptr, 2, ctypes.c_ulong)
        release(client_ptr)


def _probe_audio_endpoint_strict(flow: int, role: str, baseline: dict[str, dict[str, str]]) -> AudioEndpointReport:
    device_ptr, initialized = _get_default_endpoint(flow)
    if not device_ptr:
        _co_uninitialize_audio(initialized)
        return AudioEndpointReport(
            role=role,
            device_id="",
            friendly_name="",
            state=0,
            client_ok=False,
            mix_format_ok=False,
            volume_ok=False,
            mute=None,
            volume_scalar=None,
            baseline_id=baseline.get(role, {}).get("id"),
            baseline_name=baseline.get(role, {}).get("name"),
            baseline_match=None,
            healthy=False,
            detail="没有找到默认设备",
        )

    try:
        state = ctypes.c_ulong()
        get_state = _com_method(device_ptr, 6, ctypes.c_long, ctypes.POINTER(ctypes.c_ulong))
        hr_state = get_state(device_ptr, ctypes.byref(state))
        device_id = _read_endpoint_id(device_ptr)
        friendly_name = _read_endpoint_friendly_name(device_ptr)

        client_ptr = ctypes.c_void_p()
        activate = _com_method(device_ptr, 3, ctypes.c_long, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        hr_client = activate(device_ptr, ctypes.byref(IID_IAudioClient), CLSCTX_ALL, None, ctypes.byref(client_ptr))
        client_ok = hr_client == 0 and bool(client_ptr.value)
        mix_format_ok = client_ok
        mute, volume_scalar = _read_endpoint_mute_and_volume(device_ptr)
        volume_ok = True
        if mute is True:
            volume_ok = False
        if volume_scalar is not None and volume_scalar <= 0.02:
            volume_ok = False
        if client_ptr.value:
            release_client = _com_method(client_ptr, 2, ctypes.c_ulong)
            release_client(client_ptr)

        baseline_entry = baseline.get(role, {})
        baseline_id = baseline_entry.get("id")
        baseline_name = baseline_entry.get("name")
        baseline_match = None if not baseline_id else device_id == baseline_id
        healthy = (
            hr_state == 0
            and state.value == DEVICE_STATE_ACTIVE
            and client_ok
            and mix_format_ok
            and volume_ok
            and (baseline_match is not False)
        )
        detail_parts = [friendly_name or device_id or "未知设备", _device_state_to_text(state.value)]
        if not client_ok:
            detail_parts.append("音频接口打不开")
        if not mix_format_ok:
            detail_parts.append("混音格式拿不到")
        if mute is True:
            detail_parts.append("设备处于静音")
        if volume_scalar is not None and volume_scalar <= 0.02:
            detail_parts.append(f"音量过低({volume_scalar:.2f})")
        if baseline_match is False:
            detail_parts.append("默认设备和上次记录的不一样")
        detail = "，".join(detail_parts)
        return AudioEndpointReport(
            role=role,
            device_id=device_id,
            friendly_name=friendly_name,
            state=int(state.value),
            client_ok=client_ok,
            mix_format_ok=mix_format_ok,
            volume_ok=volume_ok,
            mute=mute,
            volume_scalar=volume_scalar,
            baseline_id=baseline_id,
            baseline_name=baseline_name,
            baseline_match=baseline_match,
            healthy=healthy,
            detail=detail,
        )
    finally:
        release = _com_method(device_ptr, 2, ctypes.c_ulong)
        release(device_ptr)
        _co_uninitialize_audio(initialized)


def _read_endpoint_id(device_ptr) -> str:
    device_id = ctypes.c_wchar_p()
    get_id = _com_method(device_ptr, 5, ctypes.c_long, ctypes.POINTER(ctypes.c_wchar_p))
    hr = get_id(device_ptr, ctypes.byref(device_id))
    if hr != 0 or not device_id.value:
        return ""
    try:
        return device_id.value
    finally:
        ctypes.windll.ole32.CoTaskMemFree(device_id)


def _get_default_endpoint(flow: int):
    initialized = _co_initialize_audio()
    enumerator = ctypes.c_void_p()
    try:
        hr = ctypes.windll.ole32.CoCreateInstance(
            ctypes.byref(CLSID_MMDeviceEnumerator),
            None,
            CLSCTX_ALL,
            ctypes.byref(IID_IMMDeviceEnumerator),
            ctypes.byref(enumerator),
        )
        if hr != 0 or not enumerator.value:
            return None, initialized

        get_default = _com_method(enumerator, 4, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        device_ptr = ctypes.c_void_p()
        hr = get_default(enumerator, flow, eConsole, ctypes.byref(device_ptr))
        if hr != 0 or not device_ptr.value:
            return None, initialized
        return device_ptr, initialized
    finally:
        if enumerator.value:
            release = _com_method(enumerator, 2, ctypes.c_ulong)
            release(enumerator)


def _probe_audio_endpoint(flow: int, role: str, baseline: dict[str, dict[str, str]]) -> AudioEndpointReport:
    device_ptr, initialized = _get_default_endpoint(flow)
    if not device_ptr:
        _co_uninitialize_audio(initialized)
        return AudioEndpointReport(
            role=role,
            device_id="",
            friendly_name="",
            state=0,
            client_ok=False,
            baseline_id=baseline.get(role, {}).get("id"),
            baseline_name=baseline.get(role, {}).get("name"),
            baseline_match=None,
            healthy=False,
            detail="没有找到默认设备",
        )

    try:
        state = ctypes.c_ulong()
        get_state = _com_method(device_ptr, 6, ctypes.c_long, ctypes.POINTER(ctypes.c_ulong))
        hr_state = get_state(device_ptr, ctypes.byref(state))
        device_id = _read_endpoint_id(device_ptr)
        friendly_name = _read_endpoint_friendly_name(device_ptr)
        client_ptr = ctypes.c_void_p()
        activate = _com_method(device_ptr, 3, ctypes.c_long, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        hr_client = activate(device_ptr, ctypes.byref(IID_IAudioClient), CLSCTX_ALL, None, ctypes.byref(client_ptr))
        client_ok = hr_client == 0 and bool(client_ptr.value)
        if client_ptr.value:
            release_client = _com_method(client_ptr, 2, ctypes.c_ulong)
            release_client(client_ptr)

        baseline_entry = baseline.get(role, {})
        baseline_id = baseline_entry.get("id")
        baseline_name = baseline_entry.get("name")
        baseline_match = None if not baseline_id else device_id == baseline_id
        healthy = hr_state == 0 and state.value == DEVICE_STATE_ACTIVE and client_ok and (baseline_match is not False)
        detail_parts = [friendly_name or device_id or "未知设备", _device_state_to_text(state.value)]
        if not client_ok:
            detail_parts.append("音频接口不可用")
        if baseline_match is False:
            detail_parts.append("默认设备和上次记录的不一样")
        detail = "，".join(detail_parts)
        return AudioEndpointReport(
            role=role,
            device_id=device_id,
            friendly_name=friendly_name,
            state=int(state.value),
            client_ok=client_ok,
            baseline_id=baseline_id,
            baseline_name=baseline_name,
            baseline_match=baseline_match,
            healthy=healthy,
            detail=detail,
        )
    finally:
        release = _com_method(device_ptr, 2, ctypes.c_ulong)
        release(device_ptr)
        _co_uninitialize_audio(initialized)


def _load_audio_baseline() -> dict[str, dict[str, str]]:
    if not AUDIO_BASELINE_FILE.exists():
        return {}
    try:
        data = json.loads(AUDIO_BASELINE_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {key: value for key, value in data.items() if isinstance(value, dict)}
    except Exception:
        pass
    return {}


def _save_audio_baseline(render: AudioEndpointReport, capture: AudioEndpointReport) -> None:
    payload = {
        "render": {"id": render.device_id, "name": render.friendly_name},
        "capture": {"id": capture.device_id, "name": capture.friendly_name},
    }
    try:
        AUDIO_BASELINE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


class AudioHealthMonitor:
    def __init__(self) -> None:
        self.baseline = _load_audio_baseline()
        self.last_good_snapshot: tuple[str, str] | None = None

    def probe(self) -> tuple[AudioEndpointReport, AudioEndpointReport]:
        render = _probe_audio_endpoint_strict(eRender, "render", self.baseline)
        capture = _probe_audio_endpoint_strict(eCapture, "capture", self.baseline)
        if render.healthy and capture.healthy and not self.baseline:
            _save_audio_baseline(render, capture)
            self.baseline = _load_audio_baseline()
        self.last_good_snapshot = (render.device_id, capture.device_id) if render.healthy and capture.healthy else self.last_good_snapshot
        return render, capture


@dataclass
class AudioEndpointReport:
    role: str
    device_id: str
    friendly_name: str
    state: int
    client_ok: bool
    mix_format_ok: bool
    volume_ok: bool
    mute: bool | None
    volume_scalar: float | None
    baseline_id: str | None
    baseline_name: str | None
    baseline_match: bool | None
    healthy: bool
    detail: str

    @property
    def status_text(self) -> str:
        if self.healthy:
            return "正常"
        if self.baseline_match is False:
            return "设备变了"
        if self.mute is True:
            return "已静音"
        if self.volume_scalar == 0:
            return "音量为0"
        return "异常"


_singleton_mutex_handle = None


def get_work_area() -> tuple[int, int, int, int]:
    rect = RECT()
    ok = ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    if ok:
        return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)
    screen_w = int(ctypes.windll.user32.GetSystemMetrics(0))
    screen_h = int(ctypes.windll.user32.GetSystemMetrics(1))
    return 0, 0, screen_w, screen_h


def get_idle_seconds() -> float:
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        return 0.0
    millis = ctypes.windll.kernel32.GetTickCount64() - info.dwTime
    return max(0.0, millis / 1000.0)


def read_power_status() -> SYSTEM_POWER_STATUS | None:
    status = SYSTEM_POWER_STATUS()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return None
    return status


def read_nt_battery_state() -> SYSTEM_BATTERY_STATE | None:
    state = SYSTEM_BATTERY_STATE()
    result = ctypes.windll.powrprof.CallNtPowerInformation(5, None, 0, ctypes.byref(state), ctypes.sizeof(state))
    if result != 0:
        return None
    return state


def get_ac_power_state_from_status(status: SYSTEM_POWER_STATUS | None) -> bool | None:
    if status is None:
        return None
    if status.ACLineStatus == 0:
        return False
    if status.ACLineStatus == 1:
        return True
    return None


def get_combined_ac_state() -> bool | None:
    status_state = get_ac_power_state_from_status(read_power_status())
    nt_state = read_nt_battery_state()
    alt_state = None if nt_state is None else bool(nt_state.AcOnLine)
    if status_state is False or alt_state is False:
        return False
    if status_state is True or alt_state is True:
        return True
    return None


def format_power_state(ac_plugged: bool | None) -> str:
    if ac_plugged is True:
        return "已插电"
    if ac_plugged is False:
        return "未插电"
    return "未知"


def describe_power_status(status: SYSTEM_POWER_STATUS | None) -> str:
    if status is None:
        return "读取失败"
    return f"{format_power_state(get_ac_power_state_from_status(status))} | 电量 {status.BatteryLifePercent}% | BatteryFlag {status.BatteryFlag}"


def describe_nt_battery_state(state: SYSTEM_BATTERY_STATE | None) -> str:
    if state is None:
        return "备用接口读取失败"
    online = "已插电" if state.AcOnLine else "未插电"
    return f"{online} | Charging {bool(state.Charging)} | Discharging {bool(state.Discharging)} | Remaining {state.RemainingCapacity}"


def ensure_single_instance() -> bool:
    global _singleton_mutex_handle
    handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not handle:
        return True
    _singleton_mutex_handle = handle
    return ctypes.windll.kernel32.GetLastError() != ERROR_ALREADY_EXISTS


def activate_existing_window() -> bool:
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, REMINDER_WINDOW_TITLE)
    if not hwnd:
        return False
    _restore_window(hwnd)
    return True


def _create_tray_icon_file() -> Path:
    icon_path = Path(tempfile.gettempdir()) / "break_reminder_tray.ico"
    png_path = icon_path.with_suffix(".png")
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return icon_path

    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((6, 6, size - 6, size - 6), radius=15, fill=(34, 117, 255, 255))
    draw.rectangle((20, 18, 28, 46), fill=(255, 255, 255, 255))
    draw.rectangle((36, 18, 44, 46), fill=(255, 255, 255, 255))
    image.save(icon_path, format="ICO")
    image.save(png_path, format="PNG")
    return icon_path


def _restore_window(hwnd: int) -> None:
    left, top, right, bottom = get_work_area()
    width, height = 420, 450
    x = max(left, right - width - 8)
    y = max(top, top + ((bottom - top - height) // 2))

    user32 = ctypes.windll.user32
    SW_RESTORE = 9
    SWP_SHOWWINDOW = 0x0040
    HWND_TOPMOST = -1
    HWND_NOTOPMOST = -2
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.MoveWindow(hwnd, x, y, width, height, True)
    user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, width, height, SWP_SHOWWINDOW)
    user32.SetWindowPos(hwnd, HWND_NOTOPMOST, x, y, width, height, SWP_SHOWWINDOW)
    user32.SetForegroundWindow(hwnd)


def _set_app_user_model_id() -> None:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Binlo.BreakReminder")
    except Exception:
        pass


class TrayIconController:
    def __init__(self, tooltip: str, on_restore_request, on_exit_request):
        self.tooltip = tooltip
        self.on_restore_request = on_restore_request
        self.on_exit_request = on_exit_request
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._restore_requested = threading.Event()
        self._exit_requested = threading.Event()
        self._thread = threading.Thread(target=self._run, name="TrayIconController", daemon=True)
        self._wndproc = None
        self._class_name = f"BreakReminderTray_{os.getpid()}"
        self._hwnd = None
        self._nid = None
        self._icon_handle = None
        self._add_ok = False
        self._start_error: Exception | None = None
        self._start_stage: str | None = None
        self._start_error_code: int | None = None
        self._registered_atom: int | None = None
        self._last_tray_message: int | None = None
        self._icon_path = _create_tray_icon_file()
        self._last_recheck = time.time()
        self._thread.start()
        self._ready.wait(timeout=5)

    def _build_notify_data(self) -> NOTIFYICONDATAW:
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self._hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        nid.uCallbackMessage = WM_TRAYICON
        nid.hIcon = self._icon_handle
        nid.szTip = self.tooltip
        return nid

    def _add_icon(self) -> None:
        shell32 = ctypes.windll.shell32
        self._nid = self._build_notify_data()
        self._add_ok = bool(shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self._nid)))
        self._nid.uTimeoutOrVersion = NOTIFYICON_VERSION_4
        shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(self._nid))
    
    def _check_and_restore_icon(self) -> bool:
        try:
            shell32 = ctypes.windll.shell32
            if not self._hwnd:
                return False
            if not self._add_ok:
                self._add_icon()
                return self._add_ok
            # 尝试修改图标来检查是否还在
            test_tip = self.tooltip + " "
            self._nid.szTip = test_tip
            result = bool(shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self._nid)))
            if not result:
                # 可能图标已经消失了，重新添加
                self._remove_icon()
                self._nid.szTip = self.tooltip
                self._add_icon()
                return self._add_ok
            # 恢复原来的提示
            self._nid.szTip = self.tooltip
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self._nid))
            return True
        except Exception:
            return False

    def _remove_icon(self) -> None:
        if self._nid is None:
            return
        try:
            ctypes.windll.shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self._nid))
        except Exception:
            pass
        self._nid = None

    def _show_context_menu(self, hwnd):
        try:
            user32 = ctypes.windll.user32
            shell32 = ctypes.windll.shell32
            
            # 获取鼠标位置
            point = POINT()
            user32.GetCursorPos(ctypes.byref(point))
            
            # 创建菜单
            hmenu = user32.CreatePopupMenu()
            if not hmenu:
                return
            
            # 添加菜单项
            MIIM_STRING = 0x00000040
            MIIM_ID = 0x00000002
            
            class MENUITEMINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_uint),
                    ('fMask', ctypes.c_uint),
                    ('fType', ctypes.c_uint),
                    ('fState', ctypes.c_uint),
                    ('wID', ctypes.c_uint),
                    ('hSubMenu', ctypes.c_void_p),
                    ('hBmpChecked', ctypes.c_void_p),
                    ('hBmpUnchecked', ctypes.c_void_p),
                    ('dwItemData', ctypes.c_ulonglong),
                    ('dwTypeData', ctypes.c_wchar_p),
                    ('cch', ctypes.c_uint),
                ]
            
            # 添加"恢复"菜单项
            mii_restore = MENUITEMINFO()
            mii_restore.cbSize = ctypes.sizeof(MENUITEMINFO)
            mii_restore.fMask = MIIM_STRING | MIIM_ID
            mii_restore.wID = 1001
            mii_restore.dwTypeData = "恢复"
            mii_restore.cch = len(mii_restore.dwTypeData)
            user32.InsertMenuItemW(hmenu, 0, True, ctypes.byref(mii_restore))
            
            # 显示菜单
            user32.SetForegroundWindow(hwnd)
            result = user32.TrackPopupMenuEx(
                hmenu, 
                0x00000040,  # TPM_RIGHTBUTTON
                point.x, 
                point.y, 
                hwnd, 
                None
            )
            
            # 处理菜单选择（只有恢复选项）
            if result == 1001:
                self._restore_requested.set()
            
            # 清理菜单
            user32.DestroyMenu(hmenu)
        except Exception:
            pass

    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg in (WM_CREATE, WM_NCCREATE):
            return 1
        if msg == WM_TRAYICON:
            self._last_tray_message = int(lparam)
            if lparam in (WM_LBUTTONUP, WM_LBUTTONDBLCLK):
                self._restore_requested.set()
            elif lparam == WM_RBUTTONUP:
                # 显示右键菜单
                self._show_context_menu(hwnd)
            return 0
        if msg == 0x0010:  # WM_CLOSE
            self._stop.set()
            ctypes.windll.user32.DestroyWindow(hwnd)
            return 0
        if msg == WM_DESTROY:
            self._remove_icon()
            ctypes.windll.user32.PostQuitMessage(0)
            return 0
        return 0

    def _run(self) -> None:
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            shell32 = ctypes.windll.shell32
            kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
            kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE
            user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
            user32.RegisterClassExW.restype = wintypes.ATOM
            user32.CreateWindowExW.argtypes = [
                wintypes.DWORD,
                wintypes.LPCWSTR,
                wintypes.LPCWSTR,
                wintypes.DWORD,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                wintypes.HWND,
                wintypes.HMENU,
                wintypes.HINSTANCE,
                ctypes.c_void_p,
            ]
            user32.CreateWindowExW.restype = wintypes.HWND
            user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
            user32.GetMessageW.restype = ctypes.c_int
            user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
            user32.TranslateMessage.restype = wintypes.BOOL
            user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
            user32.DispatchMessageW.restype = ctypes.c_ssize_t
            user32.DestroyWindow.argtypes = [wintypes.HWND]
            user32.DestroyWindow.restype = wintypes.BOOL
            user32.PostQuitMessage.argtypes = [ctypes.c_int]
            user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            user32.PostMessageW.restype = wintypes.BOOL
            shell32.Shell_NotifyIconW.argtypes = [ctypes.c_uint, ctypes.POINTER(NOTIFYICONDATAW)]
            shell32.Shell_NotifyIconW.restype = wintypes.BOOL
            shell32.Shell_NotifyIconGetRect.argtypes = [ctypes.POINTER(NOTIFYICONIDENTIFIER), ctypes.POINTER(RECT)]
            shell32.Shell_NotifyIconGetRect.restype = ctypes.c_long
            hinstance = kernel32.GetModuleHandleW(None)
            self._wndproc = WNDPROC(self._window_proc)
            wc = WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
            wc.style = 0
            wc.lpfnWndProc = self._wndproc
            wc.cbClsExtra = 0
            wc.cbWndExtra = 0
            wc.hInstance = hinstance
            wc.hIcon = None
            wc.hCursor = None
            wc.hbrBackground = None
            wc.lpszMenuName = None
            wc.lpszClassName = self._class_name
            wc.hIconSm = None
            atom = user32.RegisterClassExW(ctypes.byref(wc))
            self._registered_atom = int(atom or 0)
            if not atom:
                self._start_stage = "register_class"
                self._start_error_code = kernel32.GetLastError()
            self._hwnd = user32.CreateWindowExW(0, self._class_name, self._class_name, 0, 0, 0, 0, 0, None, None, hinstance, None)
            if not self._hwnd:
                self._start_stage = "create_window"
                self._start_error_code = kernel32.GetLastError()
                self._ready.set()
                return
            load_image = user32.LoadImageW
            load_image.restype = wintypes.HANDLE
            load_image.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
            self._icon_handle = load_image(None, str(self._icon_path), IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
            if not self._icon_handle:
                self._icon_handle = user32.LoadIconW(None, ctypes.c_wchar_p(IDI_APPLICATION))
            self._add_icon()
            self._ready.set()

            msg = MSG()
            while not self._stop.is_set():
                result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result == 0 or result == -1:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        except Exception as exc:
            self._start_error = exc
        finally:
            self._remove_icon()
            self._ready.set()

    def consume_restore_request(self) -> bool:
        if not self._restore_requested.is_set():
            return False
        self._restore_requested.clear()
        return True

    def consume_exit_request(self) -> bool:
        if not self._exit_requested.is_set():
            return False
        self._exit_requested.clear()
        return True

    def request_exit(self) -> None:
        self._exit_requested.set()
        self._stop.set()
        if self._hwnd:
            try:
                ctypes.windll.user32.PostMessageW(self._hwnd, 0x0010, 0, 0)
            except Exception:
                pass

    def request_restore(self) -> None:
        self._restore_requested.set()

    def check_and_restore(self) -> bool:
        return self._check_and_restore_icon()
    
    def get_icon_rect(self):
        if not self._hwnd:
            return None
        try:
            shell32 = ctypes.windll.shell32
            shell32.Shell_NotifyIconGetRect.argtypes = [ctypes.POINTER(NOTIFYICONIDENTIFIER), ctypes.POINTER(RECT)]
            shell32.Shell_NotifyIconGetRect.restype = ctypes.c_long
            ident = NOTIFYICONIDENTIFIER()
            ident.cbSize = ctypes.sizeof(NOTIFYICONIDENTIFIER)
            ident.hWnd = self._hwnd
            ident.uID = 1
            rect = RECT()
            hr = shell32.Shell_NotifyIconGetRect(ctypes.byref(ident), ctypes.byref(rect))
            if hr != 0:
                return None
            return rect
        except Exception:
            return None


class ReminderEngine:
    def __init__(self, continuous_target_seconds: int, idle_reset_seconds: int, session_start: dt.datetime | None = None):
        self.continuous_target_seconds = continuous_target_seconds
        self.idle_reset_seconds = idle_reset_seconds
        self.session_start = session_start or dt.datetime.now()
        self.last_sleep_reminder_date: dt.date | None = None
        self.last_power_plugged: bool | None = None

    def update(self, now: dt.datetime, idle_seconds: float, ac_plugged: bool | None) -> list[str]:
        events: list[str] = []

        if idle_seconds >= self.idle_reset_seconds:
            self.session_start = now
        else:
            continuous_seconds = (now - self.session_start).total_seconds()
            if continuous_seconds >= self.continuous_target_seconds:
                events.append("break")
                self.session_start = now

        if self._should_fire_sleep(now):
            events.append("sleep")
            self.last_sleep_reminder_date = now.date()

        if self._should_fire_power(ac_plugged):
            events.append("power")

        return events

    def current_continuous_seconds(self, now: dt.datetime, idle_seconds: float) -> int:
        if idle_seconds >= self.idle_reset_seconds:
            return 0
        return max(0, int((now - self.session_start).total_seconds()))

    def _should_fire_sleep(self, now: dt.datetime) -> bool:
        if self.last_sleep_reminder_date == now.date():
            return False
        return dt.time(23, 0) <= now.time() < dt.time(23, 1)

    def _should_fire_power(self, ac_plugged: bool | None) -> bool:
        if ac_plugged is None:
            self.last_power_plugged = None
            return False
        if ac_plugged:
            self.last_power_plugged = True
            return False
        should_fire = self.last_power_plugged is not False
        self.last_power_plugged = False
        return should_fire


class BreakReminderApp:
    def __init__(self, check_interval_ms: int, test_mode: bool, smoke_seconds: int = 0):
        target = 30 if test_mode else 3600
        reset = 8 if test_mode else 300
        self.engine = ReminderEngine(continuous_target_seconds=target, idle_reset_seconds=reset)
        self.check_interval_ms = CHECK_INTERVAL_MS if test_mode else check_interval_ms

        self.root = tk.Tk()
        self.root.title(REMINDER_WINDOW_TITLE)
        self.root.resizable(False, False)
        self.root.configure(bg="#F6F7FB")
        self.root.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        self.expanded_size = (420, 450)
        self.collapsed_size = (50, 200)
        self.is_collapsed = False
        self.current_alert: str | None = None
        self.popup_windows: list[tk.Toplevel] = []
        self.handle_window: tk.Toplevel | None = None
        self._tick_after_id: str | None = None
        self._audio_probe_at: dt.datetime = dt.datetime.min
        self._last_audio_signature: tuple[str, str] | None = None
        self._last_audio_problem_signature: str | None = None
        self._startup_visible_after_id: str | None = None
        self.audio_monitor = AudioHealthMonitor()
        self._icon_path = _create_tray_icon_file()

        self.status_var = tk.StringVar(value="状态：正常")
        self.detail_var = tk.StringVar(value="还没到提醒时间，继续专注。")
        self.usage_var = tk.StringVar(value="连续使用：00:00")
        self.next_var = tk.StringVar(value="下一次休息提醒：01:00:00")
        self.power_var = tk.StringVar(value="供电状态：读取中")
        self.raw_power_var = tk.StringVar(value="系统上报：读取中")
        self.alt_power_var = tk.StringVar(value="备用接口：读取中")
        self.render_var = tk.StringVar(value="声音：检查中")
        self.capture_var = tk.StringVar(value="麦克风：检查中")
        self.audio_detail_var = tk.StringVar(value="默认设备：检查中")

        self._set_window_icon()
        self._apply_app_icon()
        self._build_expanded_ui()
        self._refresh_audio_status(force=True)
        self.root.bind("<Map>", self._on_window_mapped, add="+")
        self.root.bind("<Unmap>", self._on_window_unmapped, add="+")
        
        # 立即确保窗口可见，避免启动时尺寸不正确
        self._ensure_window_visible()
        self._startup_visible_after_id = self.root.after(120, self._ensure_window_visible)
        self.root.after(700, self._ensure_window_visible)
        self.root.after(1500, self._ensure_window_visible)
        self.root.after(5000, self._visibility_guard_tick)
        
        # 初始化系统托盘图标
        self._tray_icon = TrayIconController(
            tooltip="休息提醒 - 点击恢复",
            on_restore_request=lambda: self.root.after(0, self._expand_widget),
            on_exit_request=lambda: self.root.after(0, self._close_app)
        )

        if smoke_seconds > 0:
            self.root.after(smoke_seconds * 1000, self._close_app)

    def _build_expanded_ui(self) -> None:
        self.root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}")
        for child in self.root.winfo_children():
            child.destroy()

        container = tk.Frame(self.root, bg="#F6F7FB", padx=14, pady=14)
        container.pack(fill="both", expand=True)

        tk.Label(container, text=WIDGET_HEADER, font=("Microsoft YaHei UI", 12, "bold"), bg="#F6F7FB", fg="#1F2A44").pack(anchor="w")
        tk.Label(container, textvariable=self.status_var, font=("Microsoft YaHei UI", 11, "bold"), bg="#F6F7FB", fg="#D7263D", pady=4).pack(anchor="w")
        tk.Label(container, textvariable=self.detail_var, font=("Microsoft YaHei UI", 11), bg="#F6F7FB", fg="#2F3A4F", justify="left", wraplength=390).pack(anchor="w", pady=(0, 6))
        tk.Label(container, textvariable=self.usage_var, font=("Microsoft YaHei UI", 11), bg="#F6F7FB", fg="#2F3A4F").pack(anchor="w")
        tk.Label(container, textvariable=self.next_var, font=("Microsoft YaHei UI", 11), bg="#F6F7FB", fg="#2F3A4F", pady=2).pack(anchor="w")
        tk.Label(container, textvariable=self.power_var, font=("Microsoft YaHei UI", 11), bg="#F6F7FB", fg="#2F3A4F").pack(anchor="w")
        tk.Label(container, textvariable=self.raw_power_var, font=("Microsoft YaHei UI", 10), bg="#F6F7FB", fg="#5C677D", wraplength=390, justify="left").pack(anchor="w", pady=(2, 0))
        tk.Label(container, textvariable=self.alt_power_var, font=("Microsoft YaHei UI", 10), bg="#F6F7FB", fg="#5C677D", wraplength=390, justify="left").pack(anchor="w", pady=(1, 0))
        tk.Label(container, textvariable=self.render_var, font=("Microsoft YaHei UI", 10), bg="#F6F7FB", fg="#5C677D", wraplength=390, justify="left").pack(anchor="w", pady=(2, 0))
        tk.Label(container, textvariable=self.capture_var, font=("Microsoft YaHei UI", 10), bg="#F6F7FB", fg="#5C677D", wraplength=390, justify="left").pack(anchor="w", pady=(1, 0))
        tk.Label(container, textvariable=self.audio_detail_var, font=("Microsoft YaHei UI", 10), bg="#F6F7FB", fg="#5C677D", wraplength=390, justify="left").pack(anchor="w", pady=(1, 0))

        btn_row = tk.Frame(container, bg="#F6F7FB")
        btn_row.pack(fill="x", pady=(12, 0))
        tk.Button(btn_row, text="隐藏", width=8, command=self._collapse_widget).pack(side="left")
        tk.Button(btn_row, text="知道了", width=8, command=self._clear_alert).pack(side="left", padx=(8, 0))

    def _build_collapsed_ui(self) -> None:
        return

    def _dock_to_right(self, width: int, height: int) -> None:
        left, top, right, bottom = get_work_area()
        x = max(left, right - width - 8)
        y = max(top, top + ((bottom - top - height) // 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _dock_handle_to_right(self) -> None:
        return

    def _ensure_window_visible(self) -> None:
        if self.is_collapsed:
            if self.root.winfo_exists():
                try:
                    if self.root.state() != "iconic":
                        pass
                except tk.TclError:
                    pass
            return

        if not self.root.winfo_exists():
            return
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            width = self.expanded_size[0]
            height = self.expanded_size[1]
            self._dock_to_right(width, height)
            self.root.update_idletasks()

            hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            SW_RESTORE = 9
            SWP_SHOWWINDOW = 0x0040
            left, top, right, bottom = get_work_area()
            x = max(left, right - width - 8)
            y = max(top, top + ((bottom - top - height) // 2))
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetWindowPos(hwnd, 0, x, y, width, height, SWP_SHOWWINDOW)
            user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def _visibility_guard_tick(self) -> None:
        if not self.root.winfo_exists():
            return
        if self.is_collapsed:
            self.root.after(5000, self._visibility_guard_tick)
            return
        try:
            needs_restore = self.root.state() != "normal"
        except tk.TclError:
            needs_restore = True
        if not needs_restore:
            try:
                self.root.update_idletasks()
                x, y = self.root.winfo_x(), self.root.winfo_y()
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                left, top, right, bottom = get_work_area()
                if x < left - 4 or y < top - 4 or x + width > right + 4 or y + height > bottom + 4:
                    needs_restore = True
            except tk.TclError:
                needs_restore = True
        if needs_restore:
            self._ensure_window_visible()
        self.root.after(5000, self._visibility_guard_tick)

    def _refresh_audio_status(self, force: bool = False) -> None:
        now = dt.datetime.now()
        if not force and (now - self._audio_probe_at).total_seconds() < 5:
            return
        self._audio_probe_at = now
        render, capture = self.audio_monitor.probe()
        self.render_var.set(
            f"声音：{render.status_text} | {render.friendly_name or render.device_id or '未知'} | "
            f"mute={render.mute} | volume={render.volume_scalar} | mix={render.mix_format_ok}"
        )
        self.capture_var.set(
            f"麦克风：{capture.status_text} | {capture.friendly_name or capture.device_id or '未知'} | "
            f"mute={capture.mute} | volume={capture.volume_scalar} | mix={capture.mix_format_ok}"
        )
        baseline_text = []
        if render.baseline_name:
            baseline_text.append(f"声音设备：{render.baseline_name}")
        if capture.baseline_name:
            baseline_text.append(f"麦克风：{capture.baseline_name}")
        if not baseline_text:
            baseline_text.append("默认设备：未知")
        self.audio_detail_var.set(" | ".join(baseline_text))

        current_signature = (render.status_text, capture.status_text)
        problem_signature = None
        if not render.healthy or not capture.healthy:
            problem_signature = f"{render.detail} / {capture.detail}"
        if problem_signature and problem_signature != self._last_audio_problem_signature:
            self._last_audio_problem_signature = problem_signature
            if self.current_alert is None:
                self.detail_var.set(f"声音/麦克风异常：{problem_signature}")
                self.status_var.set("状态：音频异常")
                self.root.configure(bg="#FFE8CC")
                self._show_popup(
                    "音频设备异常",
                    "检测到声音或麦克风设备异常，\n请检查您的音频设备设置。",
                )
        elif not problem_signature and self._last_audio_problem_signature is not None:
            self._last_audio_problem_signature = None
            if self.current_alert is None:
                self.status_var.set("状态：正常")
                self.detail_var.set("音频设备已恢复正常。")
                self.root.configure(bg="#F6F7FB")
        self._last_audio_signature = current_signature

    def _collapse_widget(self) -> None:
        self.is_collapsed = True
        if self._startup_visible_after_id is not None:
            try:
                self.root.after_cancel(self._startup_visible_after_id)
            except tk.TclError:
                pass
            self._startup_visible_after_id = None
        if self.root.winfo_exists():
            try:
                self.root.iconify()
            except tk.TclError:
                pass

    def _on_window_mapped(self, event: tk.Event | None = None) -> None:
        if not self.root.winfo_exists():
            return
        try:
            if self.root.state() != "iconic":
                self.is_collapsed = False
        except tk.TclError:
            pass

    def _on_window_unmapped(self, event: tk.Event | None = None) -> None:
        if not self.root.winfo_exists():
            return
        try:
            if self.root.state() == "iconic":
                self.is_collapsed = True
        except tk.TclError:
            pass

    def _expand_widget(self) -> None:
        self.is_collapsed = False
        self._build_expanded_ui()
        self._ensure_window_visible()

    def _hide_to_tray(self) -> None:
        self._collapse_widget()

    def _clear_alert(self) -> None:
        self.current_alert = None
        self.status_var.set("状态：正常")
        self.detail_var.set("提醒已经确认。还没到下一次提醒时间。")
        self.root.configure(bg="#F6F7FB")

    def _clear_power_alert_if_recovered(self, ac_plugged: bool | None) -> None:
        if self.current_alert != "power" or ac_plugged is not True:
            return
        self.current_alert = None
        self.status_var.set("状态：正常")
        self.detail_var.set("供电已经恢复正常。还没到下一次提醒时间。")
        self.root.configure(bg="#F6F7FB")

    def _close_app(self) -> None:
        if self._tick_after_id is not None and self.root.winfo_exists():
            try:
                self.root.after_cancel(self._tick_after_id)
            except tk.TclError:
                pass
            self._tick_after_id = None
        if self._startup_visible_after_id is not None and self.root.winfo_exists():
            try:
                self.root.after_cancel(self._startup_visible_after_id)
            except tk.TclError:
                pass
            self._startup_visible_after_id = None
        for popup in list(self.popup_windows):
            if popup.winfo_exists():
                popup.destroy()
        
        # 清理临时图标文件
        try:
            if hasattr(self, '_icon_path') and self._icon_path.exists():
                self._icon_path.unlink()
            png_path = self._icon_path.with_suffix(".png") if hasattr(self, "_icon_path") else None
            if png_path and png_path.exists():
                png_path.unlink()
        except Exception:
            pass
        
        # 释放互斥体
        global _singleton_mutex_handle
        if _singleton_mutex_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(_singleton_mutex_handle)
                _singleton_mutex_handle = None
            except Exception:
                pass
        
        # 清理托盘图标
        if hasattr(self, '_tray_icon') and self._tray_icon:
            try:
                self._tray_icon.request_exit()
            except Exception:
                pass
        
        if self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()

    def _apply_app_icon(self) -> None:
        try:
            self.root.iconbitmap(str(self._icon_path))
        except Exception:
            pass

    def _set_window_icon(self) -> None:
        try:
            photo = tk.PhotoImage(file=str(self._icon_path.with_suffix(".png")))
            self.root.iconphoto(True, photo)
            self._window_icon_ref = photo
        except Exception:
            self._window_icon_ref = None

    def run(self) -> None:
        self._tick_after_id = self.root.after(self.check_interval_ms, self._tick)
        self.root.mainloop()

    def _handle_break_event(self) -> None:
        self.current_alert = "break"
        self.status_var.set("状态：该休息了")
        opened = self._open_video_url()
        if opened:
            self.detail_var.set("你已经连续使用 1 小时，视频已自动打开，休息一下吧。")
        else:
            self.detail_var.set("你已经连续使用 1 小时，请休息一下。视频没有自动打开。")
        self.root.configure(bg="#FFF2CC")
        self._play_reminder_sound()
        self._show_popup("休息提醒", "你已经连续使用 1 小时。\n请休息一下，做一套眼保健操。", action_text="打开视频", action_cmd=self._open_video_url)

    def _handle_sleep_event(self) -> None:
        self.current_alert = "sleep"
        self.status_var.set("状态：该睡觉了")
        self.detail_var.set("现在已经 23:00，建议你准备睡觉，早点休息。")
        self.root.configure(bg="#FFE3E3")
        self._play_reminder_sound()
        self._show_popup("睡觉提醒", "已经过了 23:00。\n该准备睡觉了，早点休息。")

    def _handle_power_event(self) -> None:
        self.current_alert = "power"
        self.status_var.set("状态：电脑没插电")
        self.detail_var.set("电脑现在没有充上电。请尽快插上电源，避免突然没电。")
        self.root.configure(bg="#FFE8CC")
        self._play_reminder_sound()
        self._show_popup("充电提醒", "电脑现在没有充上电。\n请尽快插上电源，避免突然没电。")

    @staticmethod
    def _fmt_seconds(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _tick(self) -> None:
        now = dt.datetime.now()
        idle_seconds = get_idle_seconds()
        status = read_power_status()
        nt_state = read_nt_battery_state()
        ac_plugged = get_combined_ac_state()
        events = self.engine.update(now, idle_seconds, ac_plugged)
        self._clear_power_alert_if_recovered(ac_plugged)
        self._refresh_audio_status()

        continuous_seconds = self.engine.current_continuous_seconds(now, idle_seconds)
        remaining = max(0, self.engine.continuous_target_seconds - continuous_seconds)
        self.usage_var.set(f"连续使用：{self._fmt_seconds(continuous_seconds)}")
        self.next_var.set(f"下一次休息提醒：{self._fmt_seconds(remaining)}")
        self.power_var.set(f"供电状态：{format_power_state(ac_plugged)}")
        self.raw_power_var.set(f"系统上报：{describe_power_status(status)}")
        self.alt_power_var.set(f"备用接口：{describe_nt_battery_state(nt_state)}")

        for event in events:
            if event == "break":
                self._handle_break_event()
            elif event == "sleep":
                self._handle_sleep_event()
            elif event == "power":
                self._handle_power_event()

        if self.root.winfo_exists():
            # 检查托盘图标请求
            if hasattr(self, '_tray_icon') and self._tray_icon:
                try:
                    if self._tray_icon.consume_restore_request():
                        self._expand_widget()
                    if self._tray_icon.consume_exit_request():
                        self._close_app()
                    # 定期检查并恢复托盘图标（每30秒）
                    if (now.second % 30) == 0:
                        self._tray_icon.check_and_restore()
                except Exception:
                    pass
            self._tick_after_id = self.root.after(self.check_interval_ms, self._tick)

    def _play_reminder_sound(self) -> None:
        def worker() -> None:
            try:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except RuntimeError:
                pass
            try:
                for freq in (880, 988, 1046):
                    winsound.Beep(freq, 220)
            except RuntimeError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _show_popup(self, title: str, message: str, action_text: str | None = None, action_cmd=None) -> None:
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.attributes("-topmost", True)
        popup.resizable(False, False)
        self.popup_windows.append(popup)
        popup.protocol("WM_DELETE_WINDOW", lambda: self._destroy_popup(popup))

        width, height = 360, 170
        left, top, right, bottom = get_work_area()
        x = max(left, left + ((right - left - width) // 2))
        y = max(top, top + ((bottom - top - height) // 2))
        popup.geometry(f"{width}x{height}+{x}+{y}")

        frame = tk.Frame(popup, padx=16, pady=14)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=message, justify="left", font=("Microsoft YaHei UI", 10)).pack(anchor="w", pady=(0, 12))

        btn_row = tk.Frame(frame)
        btn_row.pack(fill="x")
        if action_text and action_cmd:
            tk.Button(btn_row, text=action_text, width=12, command=action_cmd).pack(side="left")
        tk.Button(btn_row, text="知道了", width=12, command=lambda: self._destroy_popup(popup)).pack(side="right")

    def _destroy_popup(self, popup: tk.Toplevel) -> None:
        if popup in self.popup_windows:
            self.popup_windows.remove(popup)
        if popup.winfo_exists():
            popup.destroy()

    def _open_video_url(self) -> bool:
        try:
            result = ctypes.windll.shell32.ShellExecuteW(None, "open", VIDEO_URL, None, None, 1)
            if result > 32:
                return True
        except Exception:
            pass
        try:
            if webbrowser.open(VIDEO_URL, new=2, autoraise=True):
                return True
        except Exception:
            pass
        try:
            os.startfile(VIDEO_URL)  # type: ignore[attr-defined]
            return True
        except Exception:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", "", VIDEO_URL])
            return True
        except Exception:
            return False


def install_autostart() -> str:
    script = Path(__file__).resolve()
    python_exe = Path(sys.executable)
    pythonw = python_exe.with_name("pythonw.exe")
    launcher = pythonw if pythonw.exists() else python_exe
    command = f'"{launcher}" "{script}"'
    startup_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    launcher_file = startup_dir / "BreakReminderApp.vbs"
    batch_file = startup_dir / "BreakReminderApp.bat"

    results: list[str] = []
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "BreakReminderApp", 0, winreg.REG_SZ, command)
            saved_value, _ = winreg.QueryValueEx(key, "BreakReminderApp")
        if saved_value == command:
            results.append("registry")
    except OSError:
        pass

    try:
        startup_dir.mkdir(parents=True, exist_ok=True)
        # 创建VBS启动文件
        temp_file = launcher_file.with_suffix(".vbs.tmp")
        temp_file.write_text(
            'Set WshShell = CreateObject("WScript.Shell")\r\n'
            f'WshShell.Run """" & "{launcher}" & """ """ & "{script}" & """", 0, False\r\n',
            encoding="utf-16",
        )
        try:
            launcher_file.unlink()
        except OSError:
            pass
        temp_file.replace(launcher_file)
        results.append("startup-vbs")
        
        # 也创建一个批处理文件作为备用
        try:
            batch_temp = batch_file.with_suffix(".bat.tmp")
            batch_temp.write_text(
                f'@echo off\r\nstart "" {command}\r\n',
                encoding="gbk",
            )
            try:
                batch_file.unlink()
            except OSError:
                pass
            batch_temp.replace(batch_file)
            results.append("startup-bat")
        except OSError:
            pass
    except OSError:
        pass

    if results:
        return "+".join(results)
    return "failed"


def ensure_autostart() -> None:
    try:
        install_autostart()
    except OSError:
        pass


def run_self_test() -> None:
    base = dt.datetime(2026, 4, 7, 22, 59, 40)
    engine = ReminderEngine(continuous_target_seconds=10, idle_reset_seconds=3, session_start=base)
    assert engine.update(base + dt.timedelta(seconds=5), idle_seconds=0, ac_plugged=True) == []
    assert engine.update(base + dt.timedelta(seconds=11), idle_seconds=0, ac_plugged=True) == ["break"]
    assert engine.update(base + dt.timedelta(seconds=12), idle_seconds=5, ac_plugged=True) == []
    assert engine.update(dt.datetime(2026, 4, 7, 23, 0, 0), idle_seconds=0, ac_plugged=True) == ["sleep"]
    assert engine.update(dt.datetime(2026, 4, 7, 23, 0, 11), idle_seconds=0, ac_plugged=True) == ["break"]
    assert engine.update(dt.datetime(2026, 4, 7, 23, 10, 0), idle_seconds=0, ac_plugged=True) == ["break"]
    print("self-test passed")


def print_power_status(watch_seconds: int = 0) -> None:
    loops = max(1, watch_seconds if watch_seconds > 0 else 1)
    for idx in range(loops):
        status = read_power_status()
        nt_state = read_nt_battery_state()
        print(
            f"{idx + 1}: 主接口[{describe_power_status(status)}] "
            f"备用接口[{describe_nt_battery_state(nt_state)}] "
            f"合并[{format_power_state(get_combined_ac_state())}]"
        )
        if idx + 1 < loops:
            time.sleep(1)


def _click_screen_point(x: int, y: int) -> None:
    user32 = ctypes.windll.user32
    user32.SetCursorPos(x, y)
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_uint),
            ("dwFlags", ctypes.c_uint),
            ("time", ctypes.c_uint),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_uint),
            ("mi", MOUSEINPUT),
        ]

    inputs = (INPUT * 2)()
    inputs[0].type = 0
    inputs[0].mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, None)
    inputs[1].type = 0
    inputs[1].mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, None)
    user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.SendInput.restype = ctypes.c_uint
    user32.SendInput(2, inputs, ctypes.sizeof(INPUT))


def _click_taskbar_point(x: int, y: int) -> bool:
    user32 = ctypes.windll.user32
    shell = user32.FindWindowW("Shell_TrayWnd", None)
    if not shell:
        return False
    tasklist = user32.FindWindowExW(shell, 0, "MSTaskListWClass", None)
    if not tasklist:
        return False

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    pt = POINT(x, y)
    if not user32.ScreenToClient(tasklist, ctypes.byref(pt)):
        return False
    lparam = (pt.y << 16) | (pt.x & 0xFFFF)
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    MK_LBUTTON = 0x0001
    user32.SendMessageW(tasklist, WM_MOUSEMOVE, 0, lparam)
    user32.SendMessageW(tasklist, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    user32.SendMessageW(tasklist, WM_LBUTTONUP, 0, lparam)
    return True


def _press_escape() -> None:
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("ki", KEYBDINPUT),
        ]

    inputs = (INPUT * 2)()
    inputs[0].type = 1
    inputs[0].ki = KEYBDINPUT(0x1B, 0, 0, 0, None)
    inputs[1].type = 1
    inputs[1].ki = KEYBDINPUT(0x1B, 0, KEYEVENTF_KEYUP, 0, None)
    user32.SendInput(2, inputs, ctypes.sizeof(INPUT))


def _find_taskbar_button_center() -> tuple[int, int]:
    try:
        from PIL import ImageGrab
    except Exception as exc:
        raise RuntimeError(f"screen capture unavailable: {exc}") from exc

    image = ImageGrab.grab()
    width, height = image.size
    x0 = max(0, width - 420)
    y0 = max(0, height - 110)

    matches: list[tuple[int, int]] = []
    for y in range(y0, height):
        for x in range(x0, width):
            r, g, b = image.getpixel((x, y))[:3]
            if 105 <= r <= 130 and 55 <= g <= 90 and 55 <= b <= 100:
                matches.append((x, y))

    if not matches:
        for y in range(y0, height):
            for x in range(x0, width):
                r, g, b = image.getpixel((x, y))[:3]
                if r >= 220 and 100 <= g <= 180 and 100 <= b <= 190:
                    matches.append((x, y))
        if not matches:
            raise RuntimeError("taskbar button not found")

    xs = [x for x, _ in matches]
    ys = [y for _, y in matches]
    return (sum(xs) // len(xs), sum(ys) // len(ys))


def run_tray_smoke_test() -> None:
    app = BreakReminderApp(check_interval_ms=CHECK_INTERVAL_MS, test_mode=True, smoke_seconds=0)

    def fail(message: str) -> None:
        print(message, file=sys.stderr)
        try:
            app._close_app()
        finally:
            os._exit(1)

    def step_hide() -> None:
        try:
            app._hide_to_tray()
            app.root.after(800, step_click)
        except Exception as exc:
            fail(f"tray smoke hide failed: {exc}")

    def step_click() -> None:
        try:
            if app.root.state() != "iconic":
                raise RuntimeError(f"window did not minimize to taskbar, state={app.root.state()}")
            app._expand_widget()
            app.root.after(1200, step_verify)
        except Exception as exc:
            fail(f"tray smoke click failed: {exc}")

    def step_verify() -> None:
        try:
            if app.root.state() != "normal":
                raise RuntimeError("window state was not restored")
            app._close_app()
        except Exception as exc:
            fail(f"tray smoke verify failed: {exc}")

    app.root.after(400, step_hide)
    app.run()
    print("tray smoke test passed")


def run_taskbar_smoke_test() -> None:
    app = BreakReminderApp(check_interval_ms=CHECK_INTERVAL_MS, test_mode=True, smoke_seconds=0)

    def fail(message: str) -> None:
        print(message, file=sys.stderr)
        try:
            app._close_app()
        finally:
            os._exit(1)

    def step_hide() -> None:
        try:
            app._collapse_widget()
            app.root.after(900, step_click)
        except Exception as exc:
            fail(f"taskbar smoke hide failed: {exc}")

    def step_click() -> None:
        try:
            if app.root.state() != "iconic":
                raise RuntimeError(f"window did not minimize, state={app.root.state()}")
            try:
                from PIL import ImageGrab
                ImageGrab.grab().save(str(Path(__file__).with_name("taskbar_smoke_hidden.png")))
            except Exception:
                pass
            _press_escape()
            time.sleep(0.3)
            points: list[tuple[int, int]] = []
            try:
                points.append(_find_taskbar_button_center())
            except Exception:
                points.extend([(1201, 1049), (1201, 1071), (1218, 1048)])
            clicked = False
            for x, y in points:
                print(f"clicking taskbar at {x},{y}")
                if not _click_taskbar_point(x, y):
                    _click_screen_point(x, y)
                time.sleep(1.2)
                if app.root.state() != "iconic" and not app.is_collapsed:
                    clicked = True
                    break
            if not clicked and app.root.state() == "iconic":
                try:
                    from PIL import ImageGrab
                    ImageGrab.grab().save(str(Path(__file__).with_name("taskbar_smoke_after_click.png")))
                except Exception:
                    pass
                raise RuntimeError("taskbar click did not restore the window")
            app.root.after(1500, step_verify)
        except Exception as exc:
            fail(f"taskbar smoke click failed: {exc}")

    def step_verify() -> None:
        try:
            if app.root.state() == "iconic" or app.is_collapsed:
                raise RuntimeError(f"window did not restore, state={app.root.state()}, collapsed={app.is_collapsed}")
            app._close_app()
        except Exception as exc:
            fail(f"taskbar smoke verify failed: {exc}")

    app.root.after(500, step_hide)
    app.run()
    print("taskbar smoke test passed")


def print_audio_status(watch_seconds: int = 0) -> None:
    loops = max(1, watch_seconds if watch_seconds > 0 else 1)
    for idx in range(loops):
        monitor = AudioHealthMonitor()
        render, capture = monitor.probe()
        print(
            f"{idx + 1}: 声音[{render.status_text}] {render.friendly_name or render.device_id or '未知'} | "
            f"mute={render.mute} | volume={render.volume_scalar} | mix={render.mix_format_ok}"
        )
        print(
            f"{idx + 1}: 麦克风[{capture.status_text}] {capture.friendly_name or capture.device_id or '未知'} | "
            f"mute={capture.mute} | volume={capture.volume_scalar} | mix={capture.mix_format_ok}"
        )
        print(f"{idx + 1}: 说明[{render.detail} / {capture.detail}]")
        if idx + 1 < loops:
            time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="休息提醒小应用")
    parser.add_argument("--install-autostart", action="store_true", help="安装开机自启")
    parser.add_argument("--self-test", action="store_true", help="运行逻辑自测")
    parser.add_argument("--background", action="store_true", help="后台模式")
    parser.add_argument("--test-mode", action="store_true", help="测试模式（30 秒触发休息提醒）")
    parser.add_argument("--smoke-seconds", type=int, default=0, help="运行若干秒后自动退出")
    parser.add_argument("--demo-alert", choices=["break", "sleep", "power"], help="立刻预览一次提醒弹窗")
    parser.add_argument("--power-status", action="store_true", help="打印当前供电状态")
    parser.add_argument("--watch-power", type=int, default=0, help="连续打印若干秒供电状态")
    parser.add_argument("--audio-status", action="store_true", help="打印当前声音和麦克风状态")
    parser.add_argument("--watch-audio", type=int, default=0, help="连续打印若干秒声音和麦克风状态")
    parser.add_argument("--tray-smoke", action="store_true", help="运行托盘图标自动验证")
    parser.add_argument("--taskbar-smoke", action="store_true", help="运行任务栏恢复自动验证")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _set_app_user_model_id()

    # 这些特殊模式不需要启动完整应用，所以直接执行后返回
    if args.self_test:
        run_self_test()
        return
    if args.install_autostart:
        print(f"autostart installed ({install_autostart()})")
        return
    if args.power_status or args.watch_power > 0:
        print_power_status(args.watch_power)
        return
    if args.audio_status or args.watch_audio > 0:
        print_audio_status(args.watch_audio)
        return
    if args.tray_smoke:
        run_tray_smoke_test()
        return
    if args.taskbar_smoke:
        run_taskbar_smoke_test()
        return

    # 对于需要启动应用的模式（包括demo_alert和正常模式），先检查单实例
    if not ensure_single_instance():
        activate_existing_window()
        return

    # 确保开机自启动
    ensure_autostart()

    if args.demo_alert:
        app = BreakReminderApp(check_interval_ms=CHECK_INTERVAL_MS, test_mode=False, smoke_seconds=max(0, args.smoke_seconds))
        if args.demo_alert == "break":
            app._handle_break_event()
        elif args.demo_alert == "sleep":
            app._handle_sleep_event()
        else:
            app._handle_power_event()
        app.run()
        return

    # 正常启动应用
    app = BreakReminderApp(check_interval_ms=CHECK_INTERVAL_MS, test_mode=args.test_mode, smoke_seconds=max(0, args.smoke_seconds))
    app.run()


if __name__ == "__main__":
    main()
