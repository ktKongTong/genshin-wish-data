# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py','getStaticData.py','getWishData.py','utils.py','dealData.py'],
             pathex=['C:\\Users\\23709\\PycharmProjects\\genshin-wish-data'],
             binaries=[],
             datas=[('.\\index.html','.'),('.\\wordpic.png','.'),('.\\origin.png','.')],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='genshin-wish-data',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='exe.ico')
