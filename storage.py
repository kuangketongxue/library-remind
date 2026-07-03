"""
统一的 JSON 文件存储层
消除 rest_reminder.py 中重复的 JSON 读/写样板代码

线程安全：所有读写操作通过实例级 threading.Lock 串行化，
避免后台报告线程与主线程并发写同一 store 导致 key 丢失。
"""
import json
import os
import sys
import copy
import logging
import tempfile
import threading

log = logging.getLogger('rest_reminder')

if getattr(sys, 'frozen', False):
    # PyInstaller 打包：数据文件放在 AppData/RestReminder/
    _BASE_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'RestReminder')
    os.makedirs(_BASE_DIR, exist_ok=True)
else:
    # 源码运行：数据文件放在 storage.py 所在目录
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_NO_DEFAULT = object()  # sentinel：区分"未传 default" 和 "显式 default=None"


class JSONStore:
    """基于文件的 JSON 键值存储。

    所有文件路径相对于项目根目录（本文件所在目录）。
    不感知业务逻辑（如日期校验），caller 自行判断数据有效性。
    """

    def __init__(self, filename, default=_NO_DEFAULT, ensure_ascii=False, indent=None):
        self._path = os.path.join(_BASE_DIR, filename)
        self._default = default
        self._ensure_ascii = ensure_ascii
        self._indent = indent
        # 实例级锁：保护 load+save 的复合操作（如 set），避免并发写覆盖
        self._lock = threading.Lock()

    def load(self):
        """加载整个文件内容，文件不存在或解析失败时返回 default 的深拷贝。"""
        with self._lock:
            if not os.path.exists(self._path):
                if self._default is _NO_DEFAULT:
                    raise FileNotFoundError(self._path)
                return copy.deepcopy(self._default)
            try:
                with open(self._path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                # 文件损坏：记录日志而非静默吞，便于排查
                log.warning(f'[storage] JSON 解析失败 {self._path}: {e}')
                if self._default is _NO_DEFAULT:
                    raise
                return copy.deepcopy(self._default)
            except OSError as e:
                # 权限/磁盘错误：记录日志
                log.warning(f'[storage] 文件读取失败 {self._path}: {e}')
                if self._default is _NO_DEFAULT:
                    raise
                return copy.deepcopy(self._default)

    def save(self, data):
        """将 data 完整写入文件（原子写入，避免崩溃导致文件损坏）。"""
        with self._lock:
            dir_name = os.path.dirname(self._path)
            fd, tmp = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=self._ensure_ascii, indent=self._indent)
                os.replace(tmp, self._path)
            except Exception:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
                raise

    def get(self, key, default=None):
        """读取单个 key，不存在时返回 default。"""
        data = self.load()
        return data.get(key, default)

    def set(self, key, value):
        """写入单个 key（先读后写，保留其他 key 不变）。"""
        # load+save 已各自持锁，但此处需保证两步原子性，避免并发写丢 key
        with self._lock:
            if not os.path.exists(self._path):
                data = copy.deepcopy(self._default) if self._default is not _NO_DEFAULT else {}
            else:
                try:
                    with open(self._path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    data = copy.deepcopy(self._default) if self._default is not _NO_DEFAULT else {}
            data[key] = value
            dir_name = os.path.dirname(self._path)
            fd, tmp = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=self._ensure_ascii, indent=self._indent)
                os.replace(tmp, self._path)
            except Exception:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
                raise
