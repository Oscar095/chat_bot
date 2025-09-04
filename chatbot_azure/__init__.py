import azure.functions as func
import logging
from .utils.openai_handler import get_chat_response
from .utils.whatsapp_sender import send_reply
from .utils.storage_handler import registrar_chat, leer_excel_blob, obtener_historial_formato_gpt, leer_pdf_blob

# Token de verificación que debe coincidir con el configurado en Meta
VERIFY_TOKEN = "mitoken1"

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # ✅ Validación del webhook (GET)
        if req.method == "GET":
            mode = req.params.get("hub.mode")
            token = req.params.get("hub.verify_token")
            challenge = req.params.get("hub.challenge")

            if mode == "subscribe" and token == VERIFY_TOKEN:
                return func.HttpResponse(challenge, status_code=200)
            else:
                return func.HttpResponse("Error: Invalid token", status_code=403)

        # ✅ Recepción de mensajes (POST)
        if req.method == "POST":
            body = req.get_json()
            user_message = body.get("Body")  # Texto recibido por WhatsApp
            sender_id = body.get("From")     # Número de cliente

            # Registrar mensaje del usuario
            registrar_chat(sender_id, "usuario", user_message)

            # Leer Excel desde blob
            df = leer_excel_blob("precios", "precios.xlsx")  
            contexto = df.to_string(index=False)

            # Leer guion en PDF desde blob
            guion = leer_pdf_blob(contenedor="guion", blob_nombre="Guion Comercial.pdf")

            # Leer historial de conversaciones
            historial_gpt = obtener_historial_formato_gpt(sender_id)

            # Obtener respuesta del modelo
            respuesta = get_chat_response(user_message, contexto, historial=historial_gpt, guion=guion)

            # Enviar respuesta al usuario por WhatsApp
            send_reply(sender_id, respuesta)

            # Registrar respuesta del asistente
            registrar_chat(sender_id, "asistente", respuesta)

            return func.HttpResponse("EVENT_RECEIVED", status_code=200)

        return func.HttpResponse("Método no soportado", status_code=405)

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error", status_code=500)
