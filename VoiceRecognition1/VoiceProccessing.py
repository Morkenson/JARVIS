from Output.TextToSpeech import speaking
from google.cloud import speech
import io
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tts.json'

client = speech.SpeechClient()

def getInput(audio_data):
    audio_content = io.BytesIO(audio_data)
    audio = speech.RecognitionAudio(content=audio_content.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  
        sample_rate_hertz=16000,  
        language_code="en-US",  
        )    

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "

    print(transcript)
    return transcript
    

