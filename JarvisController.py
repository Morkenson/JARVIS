# The Beginning of Jarvis

import SetupWizard
import threading
import sys
import os
import Output.TextToSpeech
import VoiceRecognition.MicInput
import Ai.AiDirector
import VoiceRecognition.TextInput
import VoiceRecognition.WakeDetection
from GUI.Visualizer import start_visualizer
from GUI.Onboarding import start_onboarding_ui
from pathlib import Path
from dotenv import load_dotenv

# Add updater import
try:
    import Updater
    from GUI.UpdateDialog import show_update_dialog
    UPDATER_AVAILABLE = True
except ImportError as e:
    UPDATER_AVAILABLE = False
    print(f"[Warning] Updater module not available: {e}")


def load_env_file():
    """Load .env file from appropriate location (checks both AppData and installation directory)"""
    if getattr(sys, 'frozen', False):
        # Check AppData first (where we save)
        appdata_dir = Path(os.getenv('APPDATA', os.path.expanduser('~')))
        appdata_env = appdata_dir / 'Jarvis' / '.env'
        if appdata_env.exists():
            load_dotenv(appdata_env)
            return
        # Fallback to installation directory
        install_env = Path(sys.executable).parent / '.env'
        if install_env.exists():
            load_dotenv(install_env)
    else:
        # Running as script - use default behavior
        load_dotenv()


def check_for_updates():
    """Check for updates (blocking) and handle update if available
    
    Returns:
        True if update was installed (app should exit), False otherwise
    """
    if not UPDATER_AVAILABLE:
        return False
    
    # Skip update check in test mode
    if '--test-setup' in sys.argv or '--demo-setup' in sys.argv:
        return False
    
    try:
        # Configure your GitHub repository information here
        # Or set GITHUB_REPO_OWNER and GITHUB_REPO_NAME in .env file
        load_env_file()
        
        # CHANGE THESE to match your GitHub repository
        repo_owner = os.getenv('GITHUB_REPO_OWNER', 'Morkenson')  # Your GitHub username
        repo_name = os.getenv('GITHUB_REPO_NAME', 'JARVIS')  # Your repository name
        
        print("[Updater] Checking for updates...")
        
        # Check for updates (don't auto-install yet)
        update_info = Updater.check_and_update(
            repo_owner=repo_owner,
            repo_name=repo_name,
            auto_install=False  # We'll handle installation after user confirms
        )
        
        if update_info and update_info.get('available'):
            print(f"[Updater] Update found! {update_info['current']} -> {update_info['latest']}")
            
            # Show update dialog
            update_now = show_update_dialog(
                current_version=update_info['current'],
                latest_version=update_info['latest'],
                release_notes=update_info.get('release_notes', '')
            )
            
            if update_now:
                print("[Updater] User chose to update now. Downloading and installing...")
                # Download and install the update directly
                if update_info.get('installer_url'):
                    Updater.download_and_install_update(update_info['installer_url'])
                    return True  # Update is being installed, app will exit
            else:
                print("[Updater] User chose to update later. Continuing with current version.")
        else:
            print("[Updater] You are running the latest version")
            
    except Exception as e:
        print(f"[Updater] Error during update check: {e}")
        # Continue with app launch even if update check fails
    
    return False  # No update installed, continue with app launch


def main():
    # Check for updates on launch (blocking - waits for check to complete)
    # If update is installed, this will return True and we should exit
    if check_for_updates():
        # Update is being installed, the updater will exit the app
        return
    
    # Check for test setup flag
    test_setup = '--test-setup' in sys.argv or '--demo-setup' in sys.argv
    
    # Run setup wizard if needed (or if test mode)
    if not SetupWizard.check_setup_complete() or test_setup:
        if test_setup:
            print("\n" + "=" * 60)
            print("  JARVIS - Test Setup Mode (no changes will be saved)")
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("  JARVIS - First Time Setup Required")
            print("=" * 60 + "\n")
        # Run onboarding UI in main thread; it will close and then we start visualizer
        def on_ready():
            # Start backend in a separate thread
            threading.Thread(target=run_backend, daemon=True).start()
        def run_backend():
            Output.TextToSpeech.speaking("Hello Sir")
            Ai.AiDirector.jarvisStart()
        
        # Show onboarding UI (blocks until window closes)
        start_onboarding_ui(Output.TextToSpeech.SPEAKING_EVENT, on_ready, test_mode=test_setup)
        
        # Text input callback to process messages
        def handle_text_input(text):
            """Process text input from GUI"""
            threading.Thread(target=lambda: Ai.AiDirector.messageDetermine(text), daemon=True).start()
        
        # After onboarding window closes, start the visualizer on main thread
        visualizer_root = start_visualizer(
            Output.TextToSpeech.SPEAKING_EVENT,
            run_in_thread=False,
            text_input_callback=handle_text_input
        )
        visualizer_root.mainloop()
        return

    # Setup already complete - launch visualizer and backend
    def run_backend():
        Output.TextToSpeech.speaking("Hello Sir")
        Ai.AiDirector.jarvisStart()
    threading.Thread(target=run_backend, daemon=True).start()
    
    # Text input callback to process messages
    def handle_text_input(text):
        """Process text input from GUI"""
        threading.Thread(target=lambda: Ai.AiDirector.messageDetermine(text), daemon=True).start()
    
    # Start visualizer on main thread (keeps program running)
    visualizer_root = start_visualizer(
        Output.TextToSpeech.SPEAKING_EVENT,
        run_in_thread=False,
        text_input_callback=handle_text_input
    )
    visualizer_root.mainloop()


if __name__ == '__main__':
    main()