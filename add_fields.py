
import subprocess
import json

# 配置
node_path = r"C:\Program Files\nodejs\node.exe"
lark_cli_path = r"C:\Users\binlo\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"
base_token = "DcJzbLadCaGbGws2ZekchGHhnVe"
table_id = "tbl9DT9qniE63BH7"

# 要添加的字段
fields = [
    {
        "type": "number",
        "name": "学习时长",
        "style": {"type": "plain", "precision": 1},
        "description": "每日学习时长（小时）"
    },
    {
        "type": "number", 
        "name": "电脑使用时长",
        "style": {"type": "plain", "precision": 1},
        "description": "每日电脑使用时长（小时）"
    },
    {
        "type": "number",
        "name": "电脑故障率",
        "style": {"type": "plain", "precision": 2},
        "description": "每小时崩溃次数"
    },
    {
        "type": "number",
        "name": "崩溃次数",
        "style": {"type": "plain", "precision": 0},
        "description": "今日程序崩溃次数"
    },
    {
        "type": "number",
        "name": "设备故障次数",
        "style": {"type": "plain", "precision": 0},
        "description": "今日音频设备故障次数"
    }
]

for field in fields:
    print(f"\n正在创建字段: {field['name']}")
    cmd = [
        node_path, lark_cli_path,
        "base", "+field-create",
        "--base-token", base_token,
        "--table-id", table_id,
        "--json", json.dumps(field, ensure_ascii=False),
        "--as", "user"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"标准错误:\n{result.stderr}")
    except Exception as e:
        print(f"执行出错: {e}")
