import VoiceRecognition.VoiceProccessing
from Output.TextToSpeech import speaking

import pyaudio
from google.cloud import speech
import numpy as np
import time

client = speech.SpeechClient()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def getMicAudio():
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Listening... Speak now!")
    frames = []
    silence_threshold = 200  # Lower threshold to detect speech sooner
    silence_duration = 0.6   # Seconds of silence before stopping
    max_recording_time = 12  # Maximum recording time in seconds
    
    silence_start = None
    recording_start = time.time()
    
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        
        # Convert audio data to numpy array for analysis
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Calculate RMS (Root Mean Square) to detect volume
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Check if we're in silence
        if rms < silence_threshold:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > silence_duration:
                print("Silence detected, stopping recording...")
                break
        else:
            # Reset silence timer if we detect speech
            silence_start = None
        
        # Safety check - don't record forever
        if time.time() - recording_start > max_recording_time:
            print("Maximum recording time reached, stopping...")
            break

    #speaking("I hear you sir")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = b''.join(frames)

    return VoiceRecognition.VoiceProccessing.getInput(audio_data)

    

    

