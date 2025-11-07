# PyInstaller spec for CrossPostMe Backend
# Save as server.spec in app/backend/

# This spec file builds a onefile EXE for server.py
# Run: pyinstaller server.spec

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('backend')

a = Analysis(
    ['server.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CrossPostMeBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
