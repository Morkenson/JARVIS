import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

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
