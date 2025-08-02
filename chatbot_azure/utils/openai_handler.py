import os
from openai import AzureOpenAI

# Cargar datos desde variables de entorno
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_MODEL")
api_version = os.getenv("AZURE_OPENAI_VERSION")

# Inicializar cliente
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

def get_chat_response(user_input):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente virtual para una empresa de empaques. Responde con información clara y útil.",
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        max_tokens=4096,
        temperature=0.7,
        top_p=1.0,
        model=deployment
    )
    return response.choices[0].message.content

