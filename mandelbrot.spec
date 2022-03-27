# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['cli.py'],
             pathex=[],
             binaries=[],
             datas=[('mandelbrot/view/images/logo.ico', 'mandelbrot/view/images')],
             hiddenimports=['numpy', 'Pillow', 'cv2'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries + [('mandelbrot/view/images/logo.ico', 'mandelbrot/view/images/logo.ico', 'DATA')],
          a.zipfiles,
          a.datas,  
          [],
          name='Mandelbrot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='mandelbrot\\view\\images\\logo.ico')
