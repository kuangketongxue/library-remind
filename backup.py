"""
GitHub 私有仓库自动备份模块
- backup(): 将数据文件推送到 GitHub 私有仓库
- restore(): 从 GitHub 私有仓库恢复数据文件
"""
import os
import sys
import json
import time
import base64
import requests
import logging

log = logging.getLogger('backup')

# 需要备份的数据文件
BACKUP_FILES = [
    '.daily_log.json',
    '.review_log.json',
    '.settings.json',
    '.streak.json',
    '.stats_history.json',
]

GITHUB_API = 'https://api.github.com'


def _get_base_dir():
    """数据文件目录，与 storage.py 一致"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'RestReminder')
    return os.path.dirname(os.path.abspath(__file__))


def _headers(token):
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'RestReminder-Backup/1.0',
    }


def _get_sha(token, repo, path):
    """获取远程文件 SHA（更新时需要）"""
    url = f'{GITHUB_API}/repos/{repo}/contents/{path}'
    try:
        r = requests.get(url, headers=_headers(token), timeout=15)
        if r.status_code == 200:
            return r.json().get('sha')
    except Exception as e:
        log.warning(f'[_get_sha] {path}: {e}')
    return None


def backup(token, repo):
    """备份所有数据文件到 GitHub 仓库。
    
    Args:
        token: GitHub Personal Access Token
        repo: 'owner/repo' 格式
    
    Returns:
        (success: bool, message: str)
    """
    base_dir = _get_base_dir()
    ok, fail = [], []

    for fname in BACKUP_FILES:
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            sha = _get_sha(token, repo, fname)

            payload = {
                'message': f'backup {fname} {time.strftime("%Y-%m-%d %H:%M")}',
                'content': b64,
                'branch': 'main',
            }
            if sha:
                payload['sha'] = sha

            r = requests.put(
                f'{GITHUB_API}/repos/{repo}/contents/{fname}',
                headers=_headers(token), json=payload, timeout=30,
            )
            if r.status_code in (200, 201):
                ok.append(fname)
            else:
                err = r.json().get('message', str(r.status_code))
                fail.append(f'{fname}: {err}')
        except Exception as e:
            fail.append(f'{fname}: {e}')

    if not ok:
        return False, '; '.join(fail) if fail else '无文件可备份'
    msg = f'{len(ok)}/{len(BACKUP_FILES)} 个文件已备份'
    if fail:
        msg += f'\n失败: {"; ".join(fail)}'
    return True, msg


def restore(token, repo):
    """从 GitHub 仓库恢复所有数据文件。
    
    Args:
        token: GitHub Personal Access Token
        repo: 'owner/repo' 格式
    
    Returns:
        (success: bool, message: str)
    """
    base_dir = _get_base_dir()
    ok, fail = [], []

    for fname in BACKUP_FILES:
        try:
            r = requests.get(
                f'{GITHUB_API}/repos/{repo}/contents/{fname}',
                headers=_headers(token), timeout=15,
            )
            if r.status_code == 200:
                b64 = r.json()['content']
                content = base64.b64decode(b64).decode('utf-8')
                fpath = os.path.join(base_dir, fname)
                # 原子写入：先写临时文件再替换
                tmp = fpath + '.restore.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    f.write(content)
                os.replace(tmp, fpath)
                ok.append(fname)
            elif r.status_code == 404:
                fail.append(f'{fname}: 仓库中不存在')
            else:
                fail.append(f'{fname}: HTTP {r.status_code}')
        except Exception as e:
            fail.append(f'{fname}: {e}')

    if not ok:
        return False, '; '.join(fail) if fail else '无可恢复的文件'
    msg = f'{len(ok)}/{len(BACKUP_FILES)} 个文件已恢复\n请重启应用以加载恢复的数据'
    if fail:
        msg += f'\n失败: {"; ".join(fail)}'
    return True, msg


def validate_token(token, repo):
    """验证 token 和 repo 是否有效。返回 (valid: bool, message: str)。"""
    if not token or not repo:
        return False, 'Token 或仓库名称为空'
    if '/' not in repo:
        return False, '仓库名称格式错误（应为 owner/repo）'
    try:
        r = requests.get(
            f'{GITHUB_API}/repos/{repo}',
            headers=_headers(token), timeout=15,
        )
        if r.status_code == 200:
            return True, '连接成功'
        elif r.status_code == 404:
            return False, '仓库不存在，请先在 GitHub 创建私有仓库'
        elif r.status_code == 401:
            return False, 'Token 无效'
        else:
            return False, f'验证失败: HTTP {r.status_code}'
    except requests.exceptions.Timeout:
        return False, '连接超时，请检查网络'
    except Exception as e:
        return False, f'网络错误: {e}'
