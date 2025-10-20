from openai import OpenAI

key = "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"
client = OpenAI(api_key = key)

def getChatGPT(message):
	response = client.chat.completions.create(model="gpt-4o-mini",
										   messages=[{"role": "system", "content": "You are a helpful assistant named Jarvis answer with short a precise answers."},
																	   {"role": "user", "content": message}],
										   max_tokens=100,
										   temperature=.25,
										   response_format={"type": "text"})
	chat_response = response.choices[0].message.content
	return chat_response
