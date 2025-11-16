import VoiceRecognition.VoiceProccessing
import Output.TextToSpeech
import VoiceRecognition.TextInput

import pvporcupine
import pyaudio
import numpy as np
import pygame
import io
import os

from dotenv import load_dotenv
import sys

load_dotenv()

# Try to get Porcupine key from environment, with fallback to bundled key
accessKey = os.getenv('PORCUPINE_ACCESS_KEY')

# If not found in env and running as executable, use bundled key
if not accessKey and getattr(sys, 'frozen', False):
    # Bundled Porcupine access key (exposed for distribution)
    # Users can override by setting PORCUPINE_ACCESS_KEY in .env
    accessKey = 'SH5jcfy0tx8kUJT9gu84JNqHcW+ewMo+LtSoWDupDLrBlgARHdl4fQ=='

if not accessKey:
    raise RuntimeError("PORCUPINE_ACCESS_KEY is not set. Please set it in your .env file.")

POST_WAKE_CAPTURE_SECONDS = float(os.getenv("POST_WAKE_CAPTURE_SECONDS", "2.5"))
POST_WAKE_SILENCE_FRAMES = int(os.getenv("POST_WAKE_SILENCE_FRAMES", "20"))
POST_WAKE_SILENCE_THRESHOLD = int(os.getenv("POST_WAKE_SILENCE_THRESHOLD", "120"))

def play_wake_confirmation():
    """Play a confirmation sound when wake word is detected"""
    try:
        # Method 1: Try system beep first (most reliable)
        import winsound
        winsound.Beep(800, 300)  # 800 Hz for 300ms
        return
        
    except ImportError:
        # Method 2: Try pygame beep
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            
            # Create a simple beep using pygame
            sample_rate = 22050
            duration = 0.3
            frequency = 800
            
            # Generate sine wave
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                arr[i][0] = 32767 * np.sin(2 * np.pi * frequency * i / sample_rate)
                arr[i][1] = arr[i][0]
            
            # Convert to pygame sound
            sound = pygame.sndarray.make_sound(arr.astype(np.int16))
            sound.play()
            pygame.time.wait(int(duration * 1000))
            return
            
        except Exception as e:
            print(f"Pygame beep failed: {e}")
    
    # Method 3: Fallback to text-to-speech
    try:
        Output.TextToSpeech.speaking("Yes sir")
    except:
        # Method 4: Final fallback - print to console
        print("🔊 BEEP - Wake word detected!")

def wakeDetect():
    try:
        porcupine = pvporcupine.create(access_key = accessKey, keywords=["jarvis"])  # Replace "picovoice" with your custom wake word

        # Configure audio input
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("[INFO] Listening for wake word...")

        try:
            while True:
                # Read audio data from the microphone
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)

                # Check if wake word is detected
                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    print("[INFO] Wake word detected!")
                    
                    # Play confirmation sound
                    play_wake_confirmation()

                    # Capture audio for processing (short window, break on silence)
                    print("[INFO] Capturing speech...")
                    frames = []
                    silence_frames = 0
                    max_frames = int(porcupine.sample_rate / porcupine.frame_length * POST_WAKE_CAPTURE_SECONDS)

                    for _ in range(max_frames):
                        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                        frame_array = np.frombuffer(pcm, dtype=np.int16)
                        frames.append(frame_array)

                        rms = np.sqrt(np.mean(frame_array.astype(np.float32) ** 2))
                        if rms < POST_WAKE_SILENCE_THRESHOLD:
                            silence_frames += 1
                            if silence_frames >= POST_WAKE_SILENCE_FRAMES:
                                print("[INFO] Post-wake silence detected, stopping capture.")
                                break
                        else:
                            silence_frames = 0

                    # Combine audio frames into a single array
                    if not frames:
                        continue

                    audio_buffer = np.hstack(frames)

                    # Pass audio to your speech detection system
                    return VoiceRecognition.VoiceProccessing.getInput(audio_buffer)

        except KeyboardInterrupt:
            print("[INFO] Stopping...")
        finally:
            # Clean up resources
            stream.close()
            pa.terminate()
            porcupine.delete()
            
    except Exception as e:
        print(f"[WARNING] Picovoice wake word detection failed: {e}")
        print("[INFO] Falling back to text input mode...")
        Output.TextToSpeech.speaking("Jarvis at your service sir. Please type your command.")
        return VoiceRecognition.TextInput.getTextInput()