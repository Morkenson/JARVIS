import os
from google.cloud import texttospeech
import pygame
import io

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tts.json'

client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(language_code = "en-GB",name = "en-GB-Standard-D")
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

pygame.mixer.init()

def speaking(statement):
    synthesis_input = texttospeech.SynthesisInput(text = statement)
    response = client.synthesize_speech(input=synthesis_input,voice=voice,audio_config=audio_config)

    audio_data = io.BytesIO(response.audio_content)
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue
    
    








