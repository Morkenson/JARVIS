from operator import or_
import Ai.GPTapi
import VoiceRecognition1.MicInput
import Output.TextToSpeech
import VoiceRecognition1.TextInput
import Calendar.CalendarController
import Spotify.SpotifyController
import VoiceRecognition1.WakeDetection

def jarvisStart():
    run = True
    
    while run:
            message = VoiceRecognition1.WakeDetection.wakeDetect()
            run = messageDetermine(message)
    
    

def messageDetermine(message):
    if "gpt" in message or "chat" in message:
        activateGPT()
    if "calendar" in message or "schedule" in message:
        activateCalendar()
    if "music" in message:
        activateSpotify()
    if "shut" in message or "off" in message or "no" in message or "down" in message:
        Output.TextToSpeech.speaking("goodbye sir")
        return False
    else:
        defaultGPT(message)

    return True
        
def activateGPT():
    Output.TextToSpeech.speaking("using chat-gpt sir")
    response = Ai.GPTapi.getChatGPT(VoiceRecognition1.MicInput.getMicAudio())
    #response = Ai.GPTapi.getChatGPT(VoiceRecognition1.TextInput.getTextInput())
    #print(f"from chatGPT {response}")
    Output.TextToSpeech.speaking(response)

def activateCalendar():
    Calendar.CalendarController.startCalendar()

def activateSpotify():
    Spotify.SpotifyController.runSpotify()

def defaultGPT(message):
    response = Ai.GPTapi.getChatGPT(message)
    Output.TextToSpeech.speaking(response)

    