import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",  # current free-tier fast model
    messages=[
        {"role": "user", "content": "In one sentence, what does a RAG system do?"}
    ]
)

print(response.choices[0].message.content)
