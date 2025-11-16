from Output.TextToSpeech import speaking
from google.cloud import speech
import io
import os
import sys
from pathlib import Path


def get_tts_json_path():
    """Resolve tts.json path in both script and bundled executable modes."""
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            base_path = Path(meipass)
        else:
            base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent  # project root when running from source

    for path in [
        base_path / 'tts.json',
        Path(sys.executable).parent / 'tts.json',
        Path.cwd() / 'tts.json',
    ]:
        if path.exists():
            return str(path)
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

