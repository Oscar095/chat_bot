import azure.functions as func
import logging
from utils.openai_handler import get_chat_response
from utils.whatsapp_sender import send_reply

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_message = body.get("Body")  # Texto recibido por WhatsApp
        sender_id = body.get("From")     # Número de cliente

        respuesta = get_chat_response(user_message)
        send_reply(sender_id, respuesta)

        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error", status_code=500)
