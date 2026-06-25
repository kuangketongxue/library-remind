"""
统一的 JSON 文件存储层
消除 rest_reminder.py 中重复的 JSON 读/写样板代码
"""
import json
import os
import sys
import tempfile

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

    def load(self):
        """加载整个文件内容，文件不存在或解析失败时返回 default。"""
        if not os.path.exists(self._path):
            if self._default is _NO_DEFAULT:
                raise FileNotFoundError(self._path)
            return self._default
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            if self._default is _NO_DEFAULT:
                raise
            return self._default

    def save(self, data):
        """将 data 完整写入文件（原子写入，避免崩溃导致文件损坏）。"""
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
        data = self.load()
        data[key] = value
        self.save(data)
