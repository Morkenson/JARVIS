# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)
import pvporcupine
import os

block_cipher = None

# Manually collect all Porcupine resource files
pvporcupine_dir = os.path.dirname(pvporcupine.__file__)
resources_path = os.path.join(pvporcupine_dir, 'resources')
porcupine_resources = []
if os.path.exists(resources_path):
    # Walk through all files in resources and add them with correct path structure
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            src_full = os.path.join(root, file)
            # Get relative path from pvporcupine directory
            rel_path = os.path.relpath(src_full, pvporcupine_dir)
            # PyInstaller format: (source_full_path, dest_relative_path)
            # Use forward slashes for dest path (PyInstaller will handle conversion)
            dest_rel = os.path.join('pvporcupine', rel_path).replace('\\', '/')
            porcupine_resources.append((src_full, dest_rel))

a = Analysis(
    ['JarvisController.py'],
    pathex=['.'],
    binaries=collect_dynamic_libs('pvporcupine'),
    datas=[
        ('env.example', '.'),
        ('tts.json', '.'),  # Bundle Google Cloud TTS credentials
    ] + porcupine_resources + collect_data_files('GUI', includes=['*.py']),
    hiddenimports=[
        'pyaudio',
        'pvporcupine',
        'pygame',
        'tkinter',
        'tkinter.filedialog',
        'customtkinter',
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
    hookspath=[],  # Removed to avoid conflicts with custom hook
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
