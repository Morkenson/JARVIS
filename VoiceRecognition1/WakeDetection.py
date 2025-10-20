import VoiceRecognition1.VoiceProccessing
import Output.TextToSpeech
import VoiceRecognition1.TextInput

import pvporcupine
import pyaudio
import numpy as np
import pygame
import io
import os

accessKey = 'SH5jcfy0tx8kUJT9gu84JNqHcW+ewMo+LtSoWDupDLrBlgARHdl4fQ=='

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

                    # Capture audio for processing (e.g., 5 seconds)
                    print("[INFO] Capturing speech...")
                    frames = []
                    for _ in range(0, int(porcupine.sample_rate / porcupine.frame_length * 5)):
                        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                        frames.append(np.frombuffer(pcm, dtype=np.int16))

                    # Combine audio frames into a single array
                    audio_buffer = np.hstack(frames)

                    # Pass audio to your speech detection system
                    return VoiceRecognition1.VoiceProccessing.getInput(audio_buffer)

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
        return VoiceRecognition1.TextInput.getTextInput()