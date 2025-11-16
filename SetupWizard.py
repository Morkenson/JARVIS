"""
Setup Wizard for Jarvis - Handles first-time configuration
"""
import os
import sys
from pathlib import Path

def get_app_directory():
    """Get the directory where the app is running (executable or script location)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

def get_env_path():
    """Get the path to the .env file"""
    app_dir = get_app_directory()
    return app_dir / '.env'

def check_setup_complete():
    """Check if setup has been completed (API key exists)"""
    env_path = get_env_path()
    if not env_path.exists():
        return False
    
    # Check if OPENAI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv(env_path)
    api_key = os.getenv('OPENAI_API_KEY')
    
    return api_key and api_key.strip() and api_key != 'your-openai-api-key-here'

def validate_openai_key(api_key):
    """Validate OpenAI API key by making a test request"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key.strip())
        # Make a minimal test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True, "API key is valid!"
    except Exception as e:
        return False, f"Invalid API key: {str(e)}"

def run_setup_wizard():
    """Run the interactive setup wizard"""
    print("=" * 60)
    print("  JARVIS - Initial Setup Wizard")
    print("=" * 60)
    print()
    
    if check_setup_complete():
        print("✓ Setup already complete. API key found.")
        print()
        response = input("Do you want to reconfigure? (y/n): ").strip().lower()
        if response != 'y':
            return True
    
    print("Welcome to Jarvis! Let's get you set up.")
    print()
    print("You'll need an OpenAI API key to use ChatGPT features.")
    print("Get your key at: https://platform.openai.com/api-keys")
    print()
    
    env_path = get_env_path()
    env_example_path = get_app_directory() / 'env.example'
    
    # Read env.example as template
    env_content = ""
    if env_example_path.exists():
        with open(env_example_path, 'r') as f:
            env_content = f.read()
    else:
        # Create basic template
        env_content = """# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Microsoft Graph / Calendar
MS_GRAPH_CLIENT_ID=your-azure-app-client-id
MS_GRAPH_CLIENT_SECRET=your-azure-app-client-secret
MS_GRAPH_TENANT_ID=your-tenant-id
MS_GRAPH_USER_ID=your-email@domain.com
MS_GRAPH_SCOPES=Calendars.ReadWrite

# Spotify
SPOTIPY_CLIENT_ID=your-spotify-client-id
SPOTIPY_CLIENT_SECRET=your-spotify-client-secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

# Picovoice Porcupine (Wake Word Detection)
PORCUPINE_ACCESS_KEY=your-porcupine-access-key

# Optional: Post-wake capture settings
# POST_WAKE_CAPTURE_SECONDS=2.5
# POST_WAKE_SILENCE_FRAMES=10
# POST_WAKE_SILENCE_THRESHOLD=120
"""
    
    # Get OpenAI API key
    while True:
        api_key = input("Enter your OpenAI API key (or 'skip' to configure later): ").strip()
        
        if api_key.lower() == 'skip':
            print("\n⚠️  Setup skipped. You can configure the API key later by editing the .env file.")
            print(f"   Location: {env_path}")
            return False
        
        if not api_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
        
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys usually start with 'sk-'. Continue anyway? (y/n): ", end='')
            if input().strip().lower() != 'y':
                continue
        
        # Validate the key
        print("\nValidating API key...")
        is_valid, message = validate_openai_key(api_key)
        
        if is_valid:
            print(f"✓ {message}")
            break
        else:
            print(f"❌ {message}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return False
    
    # Update env_content with the API key
    lines = env_content.split('\n')
    updated_lines = []
    for line in lines:
        if line.startswith('OPENAI_API_KEY='):
            updated_lines.append(f'OPENAI_API_KEY={api_key}')
        else:
            updated_lines.append(line)
    
    env_content = '\n'.join(updated_lines)
    
    # Write .env file
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"\n✓ Configuration saved to: {env_path}")
        print("\n✓ Setup complete! You can now use Jarvis.")
        print()
        return True
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        print(f"   Please manually create .env file at: {env_path}")
        return False

if __name__ == '__main__':
    run_setup_wizard()

