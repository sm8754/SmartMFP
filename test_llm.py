
from openai import OpenAI

client = OpenAI(api_key="")
client.models.list()
messages = []

while True:
  content = input("User: ")
  messages.append({"role": "user", "content": content})

  chat_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages
  )

  answer = chat_response.choices[0].message.content
  print(f'ChatGPT: {answer}')
  messages.append({"role": "assistant", "content": answer})