# The Beginning of Jarvis

import SetupWizard
import threading
import sys
import Output.TextToSpeech
import VoiceRecognition.MicInput
import Ai.AiDirector
import VoiceRecognition.TextInput
import VoiceRecognition.WakeDetection
from GUI.Visualizer import start_visualizer
from GUI.Onboarding import start_onboarding_ui


def main():
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