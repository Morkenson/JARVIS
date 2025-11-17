import os
import sys
import json
import subprocess
import threading
import requests
from pathlib import Path
import version

def get_current_version():
    """Get the current installed version"""
    return version.VERSION

def get_latest_release_info(repo_owner, repo_name):
    """Get the latest release information from GitHub"""
    try:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"[Updater] Error checking for updates: {e}")
        return None

def compare_versions(current, latest):
    """Compare version strings (simple semantic versioning)
    Returns: True if latest > current, False otherwise
    """
    try:
        # Remove 'v' prefix if present
        current = current.lstrip('v')
        latest = latest.lstrip('v')
        
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        # Pad with zeros if needed
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        for c, l in zip(current_parts, latest_parts):
            if l > c:
                return True
            elif l < c:
                return False
        return False  # Versions are equal
    except:
        return False

def download_installer(download_url, save_path):
    """Download the installer from GitHub"""
    try:
        print(f"[Updater] Downloading update from {download_url}...")
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"[Updater] Progress: {percent:.1f}%", end='\r')
        
        print(f"\n[Updater] Download complete: {save_path}")
        return True
    except Exception as e:
        print(f"[Updater] Download failed: {e}")
        return False

def install_update(installer_path):
    """Run the installer and exit the current application"""
    try:
        print(f"[Updater] Launching installer: {installer_path}")
        # Run installer with /VERYSILENT flag for automatic installation
        # /SP- prevents "This will install..." prompt
        # /FORCECLOSEAPPLICATIONS closes running instances
        subprocess.Popen(
            [installer_path, "/VERYSILENT", "/SP-", "/FORCECLOSEAPPLICATIONS"],
            shell=True
        )
        # Give it a moment to start, then exit
        import time
        time.sleep(1)
        sys.exit(0)
    except Exception as e:
        print(f"[Updater] Failed to launch installer: {e}")


def download_and_install_update(installer_url):
    """Download and install an update from a given URL"""
    if not installer_url:
        print("[Updater] No installer URL provided")
        return False
    
    # Download to temp directory
    temp_dir = Path(os.environ.get('TEMP', os.path.expanduser('~')))
    installer_path = temp_dir / 'JarvisSetup_Update.exe'
    
    if download_installer(installer_url, installer_path):
        install_update(installer_path)
        return True
    
    return False

def check_and_update(repo_owner="yourusername", repo_name="JARVIS", auto_install=False):
    """Check for updates and optionally install them
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: Repository name
        auto_install: If True, automatically download and install updates
                     If False, just check and return update info
    Returns:
        dict with update info, or None if no update available
    """
    current_version = get_current_version()
    print(f"[Updater] Current version: {current_version}")
    
    release_info = get_latest_release_info(repo_owner, repo_name)
    if not release_info:
        print("[Updater] Could not check for updates")
        return None
    
    latest_version = release_info.get('tag_name', '').lstrip('v')
    print(f"[Updater] Latest version: {latest_version}")
    
    if not compare_versions(current_version, latest_version):
        print("[Updater] You are running the latest version")
        return None
    
    print(f"[Updater] Update available: {current_version} -> {latest_version}")
    
    # Find the installer download URL
    installer_url = None
    for asset in release_info.get('assets', []):
        if asset['name'] == 'JarvisSetup.exe':
            installer_url = asset['browser_download_url']
            break
    
    if not installer_url:
        print("[Updater] Installer not found in release assets")
        return {
            'available': True,
            'current': current_version,
            'latest': latest_version,
            'installer_url': None
        }
    
    if auto_install:
        # Download to temp directory
        temp_dir = Path(os.environ.get('TEMP', os.path.expanduser('~')))
        installer_path = temp_dir / 'JarvisSetup_Update.exe'
        
        if download_installer(installer_url, installer_path):
            install_update(installer_path)
    
    return {
        'available': True,
        'current': current_version,
        'latest': latest_version,
        'installer_url': installer_url,
        'release_notes': release_info.get('body', '')
    }

