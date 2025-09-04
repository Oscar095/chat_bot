import azure.functions as func
import logging
from .utils.openai_handler import get_chat_response
from .utils.whatsapp_sender import send_reply
from .utils.storage_handler import registrar_chat
from .utils.storage_handler import leer_excel_blob
from .utils.storage_handler import obtener_historial_formato_gpt
from .utils.storage_handler import leer_pdf_blob  # <-- añadido


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_message = body.get("Body")  # Texto recibido por WhatsApp
        sender_id = body.get("From")     # Número de cliente
       # Registrar mensaje del usuario
        registrar_chat(sender_id, "usuario", user_message)

        df = leer_excel_blob("precios", "precios.xlsx")  # ajusta si cambia
        contexto = df.to_string(index=False)

        # Lee el guion desde tu contenedor y blob
        # Ajusta: contenedor="guion" y blob="guion.pdf" o la ruta completa si está en una carpeta virtual.
        guion = leer_pdf_blob(contenedor="guion", blob_nombre="Guion Comercial.pdf")

        historial_gpt = obtener_historial_formato_gpt(sender_id)

        respuesta = get_chat_response(user_message, contexto, historial=historial_gpt, guion=guion)
        send_reply(sender_id, respuesta)
        # Registrar respuesta del asistente
        registrar_chat(sender_id, "asistente", respuesta)

        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error", status_code=500)