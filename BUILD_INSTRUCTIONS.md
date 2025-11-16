# Building the Jarvis Installer

This guide explains how to create a one-click installer for Jarvis.

## Prerequisites

1. **Python 3.11+** with all dependencies installed
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Inno Setup** (for Windows installer)
   - Download from: https://jrsoftware.org/isdl.php
   - Install and add `iscc.exe` to your PATH (or use full path in build script)

## Quick Build

Simply run the build script:
```bash
build_installer.bat
```

This will:
1. Install PyInstaller if needed
2. Clean previous builds
3. Create standalone executable
4. Create Windows installer (if Inno Setup is available)

## Manual Build Steps

### Step 1: Build Executable

```bash
pyinstaller jarvis.spec --clean --noconfirm
```

The executable will be created at: `dist\Jarvis\Jarvis.exe`

### Step 2: Create Installer

Open `installer.iss` in Inno Setup Compiler and click "Build" or run:

```bash
iscc installer.iss
```

The installer will be created at: `dist\JarvisSetup.exe`

## What Gets Included

- All Python modules and dependencies
- `env.example` (copied to `.env` during install)
- README.md

## User Setup After Installation

After installation, users need to:

1. Navigate to installation directory (default: `C:\Program Files\Jarvis`)
2. Edit `.env` file with their API keys:
   - `OPENAI_API_KEY`
   - `MS_GRAPH_CLIENT_ID`
   - `MS_GRAPH_CLIENT_SECRET`
   - `MS_GRAPH_TENANT_ID`
   - `SPOTIPY_CLIENT_ID`
   - `SPOTIPY_CLIENT_SECRET`
   - `PORCUPINE_ACCESS_KEY`
3. Place `tts.json` (Google Cloud credentials) in the installation directory
4. Run `Jarvis.exe` from desktop shortcut or Start Menu

## Troubleshooting

### PyInstaller Issues

- **Missing modules**: Add to `hiddenimports` in `jarvis.spec`
- **Large file size**: Normal for bundled Python apps (100-200MB)
- **Antivirus warnings**: Common with PyInstaller; users may need to whitelist

### Inno Setup Issues

- **iscc not found**: Add Inno Setup bin directory to PATH or use full path
- **Permission errors**: Run as administrator if needed

## GitHub Releases

1. Create a new release on GitHub
2. Upload `dist\JarvisSetup.exe`
3. Add release notes with installation instructions
4. Link to this README for detailed setup

## Notes

- The installer requires admin privileges (for Program Files installation)
- Users must configure `.env` file manually (API keys are sensitive)
- Consider creating a setup wizard in the future for API key configuration

