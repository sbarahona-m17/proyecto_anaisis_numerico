# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["matplotlib.backends.backend_tkagg"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["pytest", "IPython", "jupyter", "scipy"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="NumLab",
    debug=False, strip=False, upx=False, console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="NumLab")
