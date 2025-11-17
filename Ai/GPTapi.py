import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def load_env_file():
    """Load .env file from AppData or project directory."""
    if getattr(sys, 'frozen', False):
        # Prefer AppData for secrets created at runtime
        appdata_env = Path(os.getenv('APPDATA', Path.home())) / 'Jarvis' / '.env'
        if appdata_env.exists():
            load_dotenv(appdata_env)
            return

        # Fallback to installation directory
        install_env = Path(sys.executable).parent / '.env'
        if install_env.exists():
            load_dotenv(install_env)
            return
    else:
        # Running from source - use repo .env if present
        project_env = Path(__file__).parent.parent / '.env'
        if project_env.exists():
            load_dotenv(project_env)
            return

    # Final fallback: default search path
    load_dotenv()


load_env_file()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=api_key)

def getChatGPT(message):
	response = client.chat.completions.create(model="gpt-4o-mini",
										   messages=[{"role": "system", "content": "You are a helpful assistant named Jarvis, like the one in the movie Iron Man, answer with short a precise answers."},
																	   {"role": "user", "content": message}],
										   max_tokens=100,
										   temperature=.25,
										   response_format={"type": "text"})
	chat_response = response.choices[0].message.content
	return chat_response
