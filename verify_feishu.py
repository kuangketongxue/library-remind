#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书同步功能验证脚本
这个脚本不依赖 rest_reminder.py，可以独立验证飞书连接
"""
import sys
import os
import json
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("错误：缺少 requests 模块")
    print("请运行: pip install requests")
    sys.exit(1)

# 直接在脚本中定义配置
FEISHU_BASE_TOKEN = 'OgmgbdX8JaVB3WshSVFcF0hDn2c'  # 从 wiki 获取的正确 token
FEISHU_TABLE_ID = 'tbl3h08zGDkwVoqE'  # 工作时长表
FEISHU_APP_ID = 'cli_a9144a1b57f85cd6'
FEISHU_APP_SECRET = 'z3SmodRLgO7AlSzD2c51HdbxtVAZHDFB'

def get_access_token():
    """获取飞书访问令牌"""
    print('\n[1] 测试获取 access_token...')
    print('-' * 70)
    
    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        }
        
        print(f'请求URL: {url}')
        print(f'使用APP_ID: {FEISHU_APP_ID}')
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'响应内容: {json.dumps(result, ensure_ascii=False)}')
            
            if result.get('code') == 0:
                token = result['tenant_access_token']
                print('✓ 获取 access_token 成功！')
                return token
            else:
                print(f'✗ 获取 access_token 失败')
                print(f'  错误码: {result.get("code")}')
                print(f'  错误信息: {result.get("msg")}')
                return None
        else:
            print(f'✗ HTTP请求失败: {response.status_code}')
            print(f'  响应: {response.text}')
            return None
            
    except Exception as e:
        print(f'✗ 异常: {e}')
        import traceback
        traceback.print_exc()
        return None


def test_query_records(access_token):
    """测试查询记录"""
    print('\n[2] 测试查询飞书表格记录...')
    print('-' * 70)
    
    try:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        print(f'请求URL: {url}')
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'响应内容: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}')
            
            if result.get('code') == 0:
                items = result.get('data', {}).get('items', [])
                print(f'✓ 查询成功！找到 {len(items)} 条记录')
                return True
            else:
                print(f'✗ 查询失败: {result.get("msg")}')
                return False
        else:
            print(f'✗ HTTP请求失败: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'✗ 异常: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_create_record(access_token):
    """测试创建记录"""
    print('\n[3] 测试创建新记录...')
    print('-' * 70)
    
    try:
        today = datetime.now().date().isoformat()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        # 转换为 Unix 时间戳（毫秒）
        today_date = datetime.now().date()
        today_timestamp = int(datetime.combine(today_date, datetime.min.time()).timestamp() * 1000)

        record_data = {
            "fields": {
                "日期": int(today_timestamp),
                "学习时长（H）": 0.1,
                "电脑使用时长（H）": 0.1
            }
        }
        
        print(f'请求URL: {url}')
        print(f'记录数据: {json.dumps(record_data, ensure_ascii=False)}')
        
        response = requests.post(url, headers=headers, json=record_data, timeout=10)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'响应内容: {json.dumps(result, ensure_ascii=False)}')
            
            if result.get('code') == 0:
                print('✓ 创建记录成功！')
                return True
            else:
                print(f'✗ 创建失败: {result.get("msg")}')
                return False
        else:
            print(f'✗ HTTP请求失败: {response.status_code}')
            print(f'  响应: {response.text}')
            return False
            
    except Exception as e:
        print(f'✗ 异常: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    print('=' * 70)
    print('飞书同步功能验证脚本')
    print('=' * 70)
    print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'配置信息:')
    print(f'  BASE_TOKEN: {FEISHU_BASE_TOKEN}')
    print(f'  TABLE_ID: {FEISHU_TABLE_ID}')
    print(f'  APP_ID: {FEISHU_APP_ID}')
    print()
    
    # 测试1：获取 access_token
    token = get_access_token()
    if not token:
        print('\n' + '=' * 70)
        print('验证失败：无法获取 access_token')
        print('请检查 APP_ID 和 APP_SECRET 配置是否正确')
        print('=' * 70)
        return
    
    # 测试2：查询记录
    if not test_query_records(token):
        print('\n警告：查询记录失败，但继续测试创建功能...')
    
    # 测试3：创建记录
    if test_create_record(token):
        print('\n' + '=' * 70)
        print('验证成功！飞书同步功能正常工作')
        print('=' * 70)
    else:
        print('\n' + '=' * 70)
        print('验证失败：无法创建记录')
        print('请检查：')
        print('  1. 飞书应用的权限是否足够')
        print('  2. 多维表格是否存在')
        print('  3. 表格字段是否匹配（日期、学习时长、电脑使用时长 (H)）')
        print('=' * 70)


if __name__ == '__main__':
    main()
