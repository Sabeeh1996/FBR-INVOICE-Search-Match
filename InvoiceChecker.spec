# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('license_config.json', '.'), ('version.txt', '.'), ('mac_config.json', '.'), ('mac_whitelist.json', '.'), ('assets/codium_edge_logo.png', 'assets')]
binaries = []
hiddenimports = ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'openpyxl', 'openpyxl.cell', 'openpyxl.styles', 'selenium', 'selenium.webdriver', 'requests', 'PIL', 'PIL.Image', 'PIL.ImageTk']
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'numpy', 'scipy', 'pytest'],
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
    name='InvoiceChecker',
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
