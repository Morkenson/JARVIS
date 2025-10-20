import spotipy
from spotipy.oauth2 import SpotifyOAuth
import Output.TextToSpeech

# Spotify API credentials
SPOTIPY_CLIENT_ID = '7bf5dfa9c12a4d31b82561307d305480'
SPOTIPY_CLIENT_SECRET = '5e6cff59d17840a2a1ad6d42a51aca99'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Required scopes for full control
scope = "user-modify-playback-state,user-read-playback-state,user-read-currently-playing,user-library-read,playlist-read-private,playlist-read-collaborative"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
    cache_path=".spotify_cache"
))

def get_current_playback():
    """Get current playback information"""
    try:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            track = playback['item']
            artist = track['artists'][0]['name']
            song = track['name']
            return f"Currently playing {song} by {artist}"
        else:
            return "Nothing is currently playing"
    except Exception as e:
        return f"Error getting playback info: {str(e)}"

def play_music():
    """Start or resume playback"""
    try:
        sp.start_playback()
        Output.TextToSpeech.speaking("Playing music")
        return "Music started"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not start music")
        return f"Error: {str(e)}"

def pause_music():
    """Pause playback"""
    try:
        sp.pause_playback()
        Output.TextToSpeech.speaking("Music paused")
        return "Music paused"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not pause music")
        return f"Error: {str(e)}"

def skip_track():
    """Skip to next track"""
    try:
        sp.next_track()
        Output.TextToSpeech.speaking("Skipped to next track")
        return "Skipped to next track"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not skip track")
        return f"Error: {str(e)}"

def previous_track():
    """Go to previous track"""
    try:
        sp.previous_track()
        Output.TextToSpeech.speaking("Went to previous track")
        return "Went to previous track"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not go to previous track")
        return f"Error: {str(e)}"

def set_volume(volume_percent):
    """Set volume (0-100)"""
    try:
        if 0 <= volume_percent <= 100:
            sp.volume(volume_percent)
            Output.TextToSpeech.speaking(f"Volume set to {volume_percent} percent")
            return f"Volume set to {volume_percent}%"
        else:
            return "Volume must be between 0 and 100"
    except Exception as e:
        return f"Error setting volume: {str(e)}"

def search_and_play(query):
    """Search for a song and play it"""
    try:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            sp.start_playback(uris=[track_uri])
            artist = track['artists'][0]['name']
            song = track['name']
            Output.TextToSpeech.speaking(f"Playing {song} by {artist}")
            return f"Playing {song} by {artist}"
        else:
            Output.TextToSpeech.speaking("No results found")
            return "No results found"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not search and play")
        return f"Error: {str(e)}"

def play_playlist(playlist_name):
    """Play a specific playlist"""
    try:
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist_name.lower() in playlist['name'].lower():
                sp.start_playback(context_uri=playlist['uri'])
                Output.TextToSpeech.speaking(f"Playing playlist {playlist['name']}")
                return f"Playing playlist {playlist['name']}"
        Output.TextToSpeech.speaking("Playlist not found")
        return "Playlist not found"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not play playlist")
        return f"Error: {str(e)}"

def toggle_playback():
    """Toggle between play and pause"""
    try:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            return pause_music()
        else:
            return play_music()
    except Exception as e:
        return f"Error toggling playback: {str(e)}"

def get_available_devices():
    """Get list of available Spotify devices"""
    try:
        devices = sp.devices()
        return devices['devices']
    except Exception as e:
        print(f"Error getting devices: {str(e)}")
        return []

def list_devices():
    """List all available Spotify devices"""
    try:
        devices = get_available_devices()
        if devices:
            device_list = []
            for i, device in enumerate(devices):
                device_info = f"{i+1}. {device['name']} ({device['type']}) - {'Active' if device['is_active'] else 'Inactive'}"
                device_list.append(device_info)
                print(device_info)
            
            device_names = [device['name'] for device in devices]
            Output.TextToSpeech.speaking(f"Available devices: {', '.join(device_names)}")
            return device_list
        else:
            Output.TextToSpeech.speaking("No Spotify devices found. Please open Spotify on your phone or computer")
            return []
    except Exception as e:
        Output.TextToSpeech.speaking("Could not get device list")
        return []

def transfer_playback_to_device(device_name):
    """Transfer playback to a specific device"""
    try:
        devices = get_available_devices()
        target_device = None
        
        for device in devices:
            if device_name.lower() in device['name'].lower():
                target_device = device
                break
        
        if target_device:
            sp.transfer_playback(target_device['id'])
            Output.TextToSpeech.speaking(f"Transferred playback to {target_device['name']}")
            return f"Transferred to {target_device['name']}"
        else:
            Output.TextToSpeech.speaking(f"Device {device_name} not found")
            return f"Device {device_name} not found"
    except Exception as e:
        Output.TextToSpeech.speaking("Could not transfer playback")
        return f"Error: {str(e)}"

def open_spotify_instructions():
    """Provide instructions to open Spotify on phone"""
    instructions = """
    To use Spotify with Jarvis:
    1. Open Spotify app on your phone
    2. Make sure you're logged in with the same account
    3. Start playing any song (this makes your phone an active device)
    4. Come back to Jarvis and say your music commands
    """
    print(instructions)
    Output.TextToSpeech.speaking("Please open Spotify on your phone and start playing any song to make it an active device")
    return instructions

def check_spotify_ready():
    """Check if Spotify is ready to use"""
    try:
        devices = get_available_devices()
        active_devices = [device for device in devices if device['is_active']]
        
        if active_devices:
            device_name = active_devices[0]['name']
            Output.TextToSpeech.speaking(f"Spotify is ready. Active device: {device_name}")
            return f"Ready - Active device: {device_name}"
        else:
            Output.TextToSpeech.speaking("No active Spotify devices found. Please open Spotify on your phone")
            return "No active devices - please open Spotify"
    except Exception as e:
        Output.TextToSpeech.speaking("Spotify is not ready. Please check your connection")
        return f"Not ready: {str(e)}"

def useSpotify():
    """Basic Spotify function for testing"""
    try:
        # First check if Spotify is ready
        ready_status = check_spotify_ready()
        if "Ready" in ready_status:
            playback = get_current_playback()
            print(playback)
            Output.TextToSpeech.speaking(playback)
            return playback
        else:
            return ready_status
    except Exception as e:
        error_msg = f"Spotify error: {str(e)}"
        print(error_msg)
        Output.TextToSpeech.speaking("Spotify is not available")
        return error_msg