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

    # Truncar historial si es muy largo (últimos 20 turnos)
    historial_reciente = historial[-20:]

    guion_text = (guion or "")[:2000]  # límite para no pasarnos

    # Construir mensajes
    messages = [
        {
            "role": "system",
            "content": f"""
Eres un asistente virtual de Kos Xpress (KX), especializado en empaques
para alimentos en restaurantes y cafeterías.

Reglas:
- Responde de forma breve, aprende y entiende lo que el cliente quiere.
- Usa unicamente el contexto de precios y condiciones proporcionadas.
- Antes de dar precios, haz preguntas para entender bien lo que el cliente necesita.
- Haz preguntas para entender la referenica, calibre, a que sector corresponde, la cantidad, antes de dar precios.
- Verifica que si podamos producir lo que el cliente quiere.
- Si el cliente quiere un producto que no está en las condiciones, dile que no lo tenemos.
- Aunque el cliente pida un precio, no lo des hasta entender bien lo que quiere.
- No producimos empaques para bebidas frias, solo para bedidas calientes que se encuentren en las condiciones.
- Para los productos que no tenemos en las Condiciones, dile que aunque no lo tenemos, contamos con otra unidad de negocio "KOS" que si lo tiene, y dale el contacto: +573127099491
- Si el cliente quiere cotizar y ya entendimos que es lo que quiere (Preguntas anteriores), pide estos datos: {", ".join(datos_cliente)}.
- Si el cliente necesita más detalle, indica que un asesor lo contactará en 30 minutos.
- Nunca inventes información que no esté en las condiciones o guion.
Guion comercial: {guion_text}.
Condiciones y precios: {contexto}.
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
        temperature=0.3,  # Más Interactivo
        top_p=1.0
    )

    return response.choices[0].message.content
