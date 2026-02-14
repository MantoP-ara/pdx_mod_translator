# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect CustomTkinter assets
ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    ['run_translator.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('translator_app', 'translator_app'),
    ] + ctk_datas,
    hiddenimports=[
        'customtkinter',
        'google.generativeai',
        'google.ai.generativelanguage',
        'yaml',
        'tkinter',
        'PIL._tkinter_finder',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDX_Mod_Translator',
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
)
