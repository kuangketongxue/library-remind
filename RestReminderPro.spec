# -*- mode: python ; coding: utf-8 -*-
# Rest Reminder Pro — PyInstaller spec

import os
pro_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'rest-reminder-pro')

a = Analysis(
    [os.path.join(pro_dir, 'rest_reminder.py')],
    pathex=[pro_dir],
    binaries=[],
    datas=[
        (os.path.join(pro_dir, 'backend.py'), '.'),
        (os.path.join(pro_dir, 'user_settings.py'), '.'),
        (os.path.join(pro_dir, 'pro_features'), 'pro_features'),
        (os.path.join(pro_dir, 'wechat-pay.jpg'), '.'),
        (os.path.join(pro_dir, 'cute_icon.png'), '.'),
        (os.path.join(pro_dir, 'cute_icon.ico'), '.'),
    ],
    hiddenimports=['backend', 'user_settings', 'pro_features'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RestReminderPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[os.path.join(pro_dir, 'cute_icon.ico')],
)
