import os
import sys
import threading
import io
from pathlib import Path

import pygame
from google.cloud import texttospeech

# Find tts.json relative to executable or script location
def get_tts_json_path():
    """Get the path to tts.json, checking installation directory first"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - check installation directory first
        exe_dir = Path(sys.executable).parent  # This is Program Files\Jarvis (installation directory)
        
        # Check installation directory first (where installer puts files)
        installed_path = exe_dir / 'tts.json'
        if installed_path.exists():
            return str(installed_path)
        
        # Then check PyInstaller temp folder (bundled files)
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            bundled_path = Path(meipass) / 'tts.json'
            if bundled_path.exists():
                return str(bundled_path)
        
        # Fallback to current working directory
        cwd_path = Path.cwd() / 'tts.json'
        if cwd_path.exists():
            return str(cwd_path)
    else:
        # Running as script
        base_path = Path(__file__).parent.parent
        script_path = base_path / 'tts.json'
        if script_path.exists():
            return str(script_path)
    
    # Final fallback
    return 'tts.json'

tts_json_path = get_tts_json_path()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = tts_json_path

client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(language_code="en-GB", name="en-GB-Standard-D")
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

pygame.mixer.init()
_play_lock = threading.Lock()
SPEAKING_EVENT = threading.Event()
# Store estimated speaking duration for animation speed matching
_estimated_duration = 0.0  # seconds


def _play_audio(audio_bytes: bytes) -> None:
    """Load and play audio data on a background thread while keeping calls non-blocking."""
    global _estimated_duration
    with _play_lock:
        # Try to get actual audio duration from pygame Sound object before loading into mixer
        try:
            temp_buffer = io.BytesIO(audio_bytes)
            temp_sound = pygame.mixer.Sound(temp_buffer)
            _estimated_duration = temp_sound.get_length()
            temp_buffer.close()
        except:
            # Fallback: estimate from audio file size (MP3 is roughly 16KB per second at typical quality)
            _estimated_duration = len(audio_bytes) / 16000.0  # Rough estimate
        
        audio_buffer = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_buffer)
        SPEAKING_EVENT.set()
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(10)
        SPEAKING_EVENT.clear()
        _estimated_duration = 0.0


def speaking(statement):
    def synthesize_and_play():
        """Synthesize speech and play audio in background thread to avoid blocking"""
        synthesis_input = texttospeech.SynthesisInput(text=statement)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        _play_audio(response.audio_content)
    
    # Run synthesis in background thread so it doesn't block the caller
    threading.Thread(target=synthesize_and_play, daemon=True).start()


def get_estimated_duration():
    """Get the estimated speaking duration for animation speed matching"""
    return _estimated_duration
    
    








