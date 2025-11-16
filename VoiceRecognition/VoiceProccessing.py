from Output.TextToSpeech import speaking
from google.cloud import speech
import io
import os
import sys
from pathlib import Path


def get_tts_json_path():
    """Resolve tts.json path in both script and bundled executable modes."""
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
    
    return 'tts.json'


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_tts_json_path()

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

