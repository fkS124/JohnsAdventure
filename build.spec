# -*- mode: python ; coding: utf-8 -*-


import os

import data.scripts.utils.resource_path as path

_WINDOWS = "Windows"
_LINUX = "Linux"
_MAC = "Darwin"



# OS of the host that 
host_os = os_system_str

VERSION = "0.23"
ICON_PATH_KEY = f"{resource_path("data/ui/logo.ico")}"


print(f"""
Compiling John's Adventures for {host_os}....

Pyinstaller config by @mariopapaz
""")


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

print("Finished importing the data folder")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f"John's Adventure v{VERSION} {host_os}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='{ICON_PATH_KEY}'
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

print("The game has been successfully compiled.")
