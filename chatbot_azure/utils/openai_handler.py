import os
from openai import AzureOpenAI
import httpx

# Cargar datos desde variables de entorno
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_MODEL")
api_version = os.getenv("AZURE_OPENAI_VERSION")

# Inicializar cliente
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version,
    http_client=httpx.Client(trust_env=True)
)

# Datos que pediremos al cliente para una cotización
datos_cliente = ["Nombre", "Dirección", "Teléfono", "Ciudad", "Correo"]

def get_chat_response(user_input, contexto, historial=None, guion=None):
    if historial is None:
        historial = []

    # Truncar historial si es muy largo (últimos 10 turnos)
    historial_reciente = historial[-10:]  

    guion_text = (guion or "")[:2000]  # límite para no pasarnos

    # Construir mensajes
    messages = [
        {
            "role": "system",
            "content": f"""
Eres un asistente virtual de Kos Xpress (KX), especializado en empaques
para alimentos en restaurantes y cafeterías.

Reglas:
- Responde de forma breve, clara y directa.
- Usa SOLO el contexto de precios y condiciones proporcionadas en {contexto}.
- Haz preguntas para entender la Referenica, calibre, cantidad antes de dar precios.
- Si el cliente quiere cotizar, pide estos datos: {", ".join(datos_cliente)}.
- Si el cliente necesita más detalle, indica que un asesor lo contactará en 30 minutos.
- Nunca inventes información que no esté en las condiciones o guion.
Guion comercial: {guion_text}
"""
        }
    ]

    # Agregar historial real al prompt
    for msg in historial_reciente:
        messages.append(msg)

    # Agregar el último mensaje del usuario
    messages.append({"role": "user", "content": user_input})

    # Llamada al modelo
    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=500,   # Limitar longitud de la respuesta
        temperature=0.5,  # Más concreto
        top_p=1.0
    )

    return response.choices[0].message.content
