"""
统一的 JSON 文件存储层
消除 rest_reminder.py 中重复的 JSON 读/写样板代码
"""
import json
import os


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class JSONStore:
    """基于文件的 JSON 键值存储。

    所有文件路径相对于项目根目录（本文件所在目录）。
    不感知业务逻辑（如日期校验）， caller 自行判断数据有效性。
    """

    def __init__(self, filename, default=None, ensure_ascii=False):
        self._path = os.path.join(_BASE_DIR, filename)
        self._default = default if default is not None else {}
        self._ensure_ascii = ensure_ascii

    def load(self):
        """加载整个文件内容，文件不存在或解析失败时返回 default。"""
        if not os.path.exists(self._path):
            return self._default
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._default

    def save(self, data):
        """将 data 完整写入文件（覆盖）。"""
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=self._ensure_ascii)

    def get(self, key, default=None):
        """读取单个 key，不存在时返回 default。"""
        data = self.load()
        if default is None:
            return data.get(key)
        return data.get(key, default)

    def set(self, key, value):
        """写入单个 key（先读后写，保留其他 key 不变）。"""
        data = self.load()
        data[key] = value
        self.save(data)
