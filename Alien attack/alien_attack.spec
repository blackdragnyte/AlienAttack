# alien_attack.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['alien_attack.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('s.png', '.'),
        ('vaisseau.png', '.'),
        ('pixel_laser_yellow.png', '.'),
        ('alien.png', '.'),
        ('alien1.png', '.'),
        ('alien2.png', '.'),
        ('pixel_laser_red.png', '.'),
        ('vie.png', '.'),
        ('bouclier.png', '.'),
        ('speed.png', '.'),
        ('freezer.png', '.'),
        ('warning.png', '.'),
        ('orbe.png', '.'),
      
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='alien_attack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='alien_attack',
)
