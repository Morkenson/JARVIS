# The Beginning of Jarvis

import SetupWizard
import threading
import Output.TextToSpeech
import VoiceRecognition.MicInput
import Ai.AiDirector
import VoiceRecognition.TextInput
import VoiceRecognition.WakeDetection
from GUI.Visualizer import start_visualizer
from GUI.Onboarding import start_onboarding_ui


def main():
    # Run setup wizard if needed
    if not SetupWizard.check_setup_complete():
        print("\n" + "=" * 60)
        print("  JARVIS - First Time Setup Required")
        print("=" * 60 + "\n")
        # Run onboarding UI in main thread; continue backend after save
        def on_ready():
            threading.Thread(target=run_backend, daemon=True).start()
        def run_backend():
            Output.TextToSpeech.speaking("Hello Sir")
            Ai.AiDirector.jarvisStart()
        start_onboarding_ui(Output.TextToSpeech.SPEAKING_EVENT, on_ready)
        return

    # Setup already complete - launch visualizer and backend
    def run_backend():
        Output.TextToSpeech.speaking("Hello Sir")
        Ai.AiDirector.jarvisStart()
    threading.Thread(target=run_backend, daemon=True).start()
    start_visualizer(Output.TextToSpeech.SPEAKING_EVENT)
    
    Output.TextToSpeech.speaking("Hello Sir")

    #Ai.AiDirector.messageDetermine(VoiceRecognition.MicInput.getMicAudio())
    #Ai.AiDirector.messageDetermine(VoiceRecognition.TextInput.getTextInput())
    Ai.AiDirector.jarvisStart()


if __name__ == '__main__':
    main()