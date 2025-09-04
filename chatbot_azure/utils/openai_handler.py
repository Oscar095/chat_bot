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

datos_cliente = ["Nombre: ", "Direccion: " , "Telefono: ", "Ciudad: ","Correo: "]

def get_chat_response(user_input, contexto, historial=None, guion=None):
    if historial is None:
        historial = []
    guion_text = (guion or "")[:5000]  # evita prompts demasiado largos
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""
                Eres un asistente virtual de Kos Xpress (KX), unidad enfocada en producción de pequeñas cantidades
                para emprendimientos, restaurantes y cafeterías. Usa este guion para tus respuestas: {guion_text} y ten en cuenta el historial del cliente : {historial} .
                Usa el siguiente contenido para responder: {contexto}. 
                Trata de preguntar más necesidades al cliente, no entregar la información de precios tan rápido; debes preguntar por algún calibre,
                cantidad, ciudad; entrégale las opciones que tenemos disponibles en Calibres y Cantidades.
                Si el cliente necesita más detalle, indícale que un asesor lo contactará en aprox. 30 minutos. 
                Si muestra interés en cotizar, pregúntale: “¿Deseas que te genere una cotización con base en tus productos?”. 
                Si dice sí, solicita: {datos_cliente} y genera un formato sencillo de cotización.
            """},
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
