# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

block_cipher = None

a = Analysis(
    ['JarvisController.py'],
    pathex=['.'],
    binaries=collect_dynamic_libs('pvporcupine'),
    datas=[
        ('env.example', '.'),
        ('tts.json', '.'),  # Bundle Google Cloud TTS credentials
    ] + collect_data_files('pvporcupine', includes=['resources/*']) \
      + collect_data_files('GUI', includes=['*.py']),
    hiddenimports=[
        'pyaudio',
        'pvporcupine',
        'pygame',
        'tkinter',
        'tkinter.filedialog',
        'GUI',
        'GUI.Onboarding',
        'GUI.Visualizer',
    ] + collect_submodules('GUI') + [
        'google.cloud.speech',
        'google.cloud.texttospeech',
        'openai',
        'spotipy',
        'msal',
        'numpy',
        'dotenv',
        'winsound',
        'io',
        'json',
        'threading',
        'SetupWizard',
        'pathlib',
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
    name='Jarvis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

