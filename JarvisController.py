# The Beginning of Jarvis

import Output.TextToSpeech
import VoiceRecognition1.MicInput
import Ai.AiDirector
import VoiceRecognition1.TextInput
import VoiceRecognition1.WakeDetection


def main():
    Output.TextToSpeech.speaking("Hello Sir")

    #Ai.AiDirector.messageDetermine(VoiceRecognition1.MicInput.getMicAudio())
    #Ai.AiDirector.messageDetermine(VoiceRecognition1.TextInput.getTextInput())
    Ai.AiDirector.jarvisStart()


if __name__ == '__main__':
    main()