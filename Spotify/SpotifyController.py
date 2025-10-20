import Spotify.Spotify
import VoiceRecognition1.MicInput
import Output.TextToSpeech

def runSpotify():
    """Main Spotify control function"""
    Output.TextToSpeech.speaking("What would you like?")
    
    while True:
        
        command = VoiceRecognition1.WakeDetection.wakeDetect().lower()
        Output.TextToSpeech.speaking("Listening")
        
        if not command:
            continue
            
        print(f"Spotify command: {command}")
        
        # Play/Pause commands
        if any(word in command for word in ["play", "start", "resume"]):
            if "pause" in command or "stop" in command:
                result = Spotify.Spotify.pause_music()
            else:
                result = Spotify.Spotify.play_music()
            Output.TextToSpeech.speaking(result)
            
        elif any(word in command for word in ["pause", "stop"]):
            result = Spotify.Spotify.pause_music()
            Output.TextToSpeech.speaking(result)
            
        # Track navigation
        elif any(word in command for word in ["next", "skip", "forward"]):
            result = Spotify.Spotify.skip_track()
            Output.TextToSpeech.speaking(result)
            
        elif any(word in command for word in ["previous", "back", "last"]):
            result = Spotify.Spotify.previous_track()
            Output.TextToSpeech.speaking(result)
            
        # Volume control
        elif "volume" in command:
            volume = extract_volume_from_command(command)
            if volume is not None:
                result = Spotify.Spotify.set_volume(volume)
                Output.TextToSpeech.speaking(result)
            else:
                Output.TextToSpeech.speaking("Please specify a volume level between 0 and 100")
                
        # Search and play
        elif any(word in command for word in ["play", "search"]) and any(word in command for word in ["song", "track", "music"]):
            # Extract the search query
            search_query = extract_search_query(command)
            if search_query:
                result = Spotify.Spotify.search_and_play(search_query)
                Output.TextToSpeech.speaking(result)
            else:
                Output.TextToSpeech.speaking("What song would you like me to search for?")
                
        # Playlist commands
        elif "playlist" in command:
            playlist_name = extract_playlist_name(command)
            if playlist_name:
                result = Spotify.Spotify.play_playlist(playlist_name)
                Output.TextToSpeech.speaking(result)
            else:
                Output.TextToSpeech.speaking("Which playlist would you like me to play?")
                
        # Device management commands
        elif any(word in command for word in ["devices", "device", "list"]):
            result = Spotify.Spotify.list_devices()
            
        elif "transfer" in command or "switch" in command:
            # Extract device name from command
            device_name = extract_device_name(command)
            if device_name:
                result = Spotify.Spotify.transfer_playback_to_device(device_name)
                Output.TextToSpeech.speaking(result)
            else:
                Output.TextToSpeech.speaking("Which device would you like to transfer to?")
                
        elif any(word in command for word in ["open", "phone", "mobile", "instructions"]):
            result = Spotify.Spotify.open_spotify_instructions()
            
        elif any(word in command for word in ["ready", "check", "status"]):
            result = Spotify.Spotify.check_spotify_ready()
            Output.TextToSpeech.speaking(result)
            
        # Status/Info commands
        elif any(word in command for word in ["what", "current", "playing", "info"]):
            result = Spotify.Spotify.get_current_playback()
            Output.TextToSpeech.speaking(result)
            
        # Exit commands
        elif any(word in command for word in ["exit", "quit", "done", "back", "return"]):
            Output.TextToSpeech.speaking("Exiting Spotify control")
            break
            
        else:
            Output.TextToSpeech.speaking("I didn't understand")

def extract_volume_from_command(command):
    """Extract volume percentage from voice command"""
    import re
    
    # Look for numbers in the command
    numbers = re.findall(r'\d+', command)
    if numbers:
        volume = int(numbers[0])
        if 0 <= volume <= 100:
            return volume
    
    # Look for common volume words
    if "mute" in command or "zero" in command:
        return 0
    elif "low" in command:
        return 25
    elif "medium" in command or "half" in command:
        return 50
    elif "high" in command or "loud" in command:
        return 75
    elif "max" in command or "full" in command:
        return 100
    
    return None

def extract_search_query(command):
    """Extract search query from voice command"""
    # Remove common command words
    words_to_remove = ["play", "search", "for", "song", "track", "music", "find", "the", "a", "an"]
    
    words = command.split()
    query_words = [word for word in words if word.lower() not in words_to_remove]
    
    return " ".join(query_words) if query_words else None

def extract_playlist_name(command):
    """Extract playlist name from voice command"""
    # Remove common command words
    words_to_remove = ["play", "playlist", "the", "my", "a", "an"]
    
    words = command.split()
    playlist_words = [word for word in words if word.lower() not in words_to_remove]
    
    return " ".join(playlist_words) if playlist_words else None

def extract_device_name(command):
    """Extract device name from voice command"""
    # Remove common command words
    words_to_remove = ["transfer", "switch", "to", "the", "my", "a", "an", "device"]
    
    words = command.split()
    device_words = [word for word in words if word.lower() not in words_to_remove]
    
    return " ".join(device_words) if device_words else None

