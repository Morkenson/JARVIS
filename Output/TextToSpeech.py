import os
import sys
import threading
import io
from pathlib import Path

import pygame
from google.cloud import texttospeech

# Find tts.json relative to executable or script location
def get_tts_json_path():
    """Get the path to tts.json, checking bundled location first, then app directory"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - check PyInstaller temp folder first
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            base_path = Path(meipass)  # Convert string to Path
        else:
            base_path = Path(sys.executable).parent
    else:
        # Running as script
        base_path = Path(__file__).parent.parent
    
    # Check multiple possible locations
    possible_paths = [
        base_path / 'tts.json',  # Bundled with executable
        Path(sys.executable).parent / 'tts.json',  # Same directory as executable
        Path.cwd() / 'tts.json',  # Current working directory
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Fallback to current directory
    return 'tts.json'

tts_json_path = get_tts_json_path()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = tts_json_path

client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(language_code="en-GB", name="en-GB-Standard-D")
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

pygame.mixer.init()
_play_lock = threading.Lock()
SPEAKING_EVENT = threading.Event()


def _play_audio(audio_bytes: bytes) -> None:
    """Load and play audio data on a background thread while keeping calls non-blocking."""
    with _play_lock:
        audio_buffer = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_buffer)
        SPEAKING_EVENT.set()
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(10)
        SPEAKING_EVENT.clear()


def speaking(statement):
    synthesis_input = texttospeech.SynthesisInput(text=statement)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    threading.Thread(target=_play_audio, args=(response.audio_content,), daemon=True).start()
    
    








