# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)
import pvporcupine
import os

block_cipher = None

# Manually collect all Porcupine resource files (resources, lib, etc.)
pvporcupine_dir = os.path.dirname(pvporcupine.__file__)
porcupine_resources = []

# Collect all files from pvporcupine directory (resources, lib, etc.)
if os.path.exists(pvporcupine_dir):
    # Walk through ALL directories in pvporcupine (resources, lib, etc.)
    for root, dirs, files in os.walk(pvporcupine_dir):
        # Skip __pycache__ and .py files (they're handled by hiddenimports)
        if '__pycache__' in root or root.endswith('.py'):
            continue
        
        for file in files:
            # Skip .pyc files
            if file.endswith('.pyc') or file.endswith('.pyo'):
                continue
            
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
        'Updater',
        'version',
        'requests',
        'GUI.UpdateDialog',
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
