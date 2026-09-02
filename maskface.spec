# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [
    ('models/deploy.prototxt', 'models'),
    ('models/res10_300x300_ssd_iter_140000_fp16.caffemodel', 'models'),
    ('models/face_detection_yunet_2023mar.onnx', 'models'),
    ('mask.png', '.'),
]
for pkg in ['imageio', 'moviepy', 'librosa', 'numpy', 'scipy', 'tqdm', 'soundfile', 'numba', 'llvmlite', 'scikit-learn', 'sv_ttk']:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'cv2',
        'librosa',
        'numba',
        'llvmlite',
        'soundfile',
        'imageio_ffmpeg',
        'sklearn',
        'scipy',
        'numpy',
        'tqdm',
        'PIL',
        'sv_ttk',
    ],
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
    [],
    exclude_binaries=True,
    name='MaskFace',
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
    icon=r'maskface.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MaskFace',
)