import azure.functions as func
import logging
from urllib.parse import parse_qs
from .utils.openai_handler import get_chat_response
from .utils.whatsapp_sender import send_reply
from .utils.storage_handler import registrar_chat, leer_excel_blob, obtener_historial_formato_gpt, leer_pdf_blob


# Token de verificación que debe coincidir con el configurado en Meta
VERIFY_TOKEN = "mitoken1"

def _parse_post(req: func.HttpRequest) -> dict:
    # 1) Intentar JSON
    try:
        body = req.get_json()

        # Intentar extraer desde el formato de WhatsApp Cloud API (Meta)
        try:
            # value puede venir en entry[0].changes[0].value (oficial) o directamente en body["value"] (pruebas)
            value = None
            if isinstance(body, dict):
                if "entry" in body:
                    value = (body.get("entry") or [{}])[0].get("changes", [{}])[0].get("value")
                elif "value" in body:
                    value = body.get("value")

            if isinstance(value, dict):
                msgs = value.get("messages") or []
                if msgs:
                    msg = msgs[0]
                    sender = msg.get("from") or (value.get("contacts") or [{}])[0].get("wa_id")

                    text = ""
                    mtype = msg.get("type")
                    if mtype == "text":
                        text = (msg.get("text") or {}).get("body", "")
                    elif mtype == "interactive":
                        interactive = msg.get("interactive") or {}
                        if interactive.get("type") == "button":
                            text = (interactive.get("button") or {}).get("text", "")
                        elif interactive.get("type") == "list_reply":
                            text = (interactive.get("list_reply") or {}).get("title", "")
                        else:
                            text = ""
                    else:
                        text = f"[{mtype} message]" if mtype else ""

                    if sender and text:
                        return {"Body": text, "From": sender}

            # Si no era formato Meta, pero ya viene con Body/From, respétalo
            if isinstance(body, dict) and ("Body" in body or "From" in body):
                return body
        except Exception:
            pass

    except Exception:
        pass

    # 2) Intentar como x-www-form-urlencoded
    try:
        form = parse_qs((req.get_body() or b"").decode("utf-8"))
        return {
            "Body": (form.get("Body") or [""])[0],
            "From": (form.get("From") or [""])[0],
        }
    except Exception:
        return {}

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # ✅ Validación del webhook (GET)
        if req.method == "GET":
            mode = req.params.get("hub.mode")
            token = req.params.get("hub.verify_token")
            challenge = req.params.get("hub.challenge")

            if mode == "subscribe" and token == VERIFY_TOKEN and challenge is not None:
                return func.HttpResponse(challenge, status_code=200)
            return func.HttpResponse("Error: Invalid token", status_code=403)

        # ✅ Recepción de mensajes (POST)
        if req.method == "POST":
            body = _parse_post(req)
            user_message = (body.get("Body") or "").strip()
            sender_id = (body.get("From") or "").strip()
            if not user_message or not sender_id:
                logging.warning(f"POST inválido. Body: {body}")
                return func.HttpResponse("Bad Request", status_code=400)

            # Registrar mensaje del usuario
            registrar_chat(sender_id, "usuario", user_message)

            # Leer Excel desde blob
            try:
                df = leer_excel_blob("precios", "precios.xlsx")
                contexto = df.to_string(index=False) if df is not None else ""
            except Exception as ex:
                logging.warning(f"No se pudo leer precios.xlsx: {ex}")
                contexto = ""

            # Leer guion en PDF desde blob
            try:
                guion = leer_pdf_blob(contenedor="guion", blob_nombre="Guion Comercial.pdf")
            except Exception as ex:
                logging.warning(f"No se pudo leer guion PDF: {ex}")
                guion = ""

            # Leer historial de conversaciones
            historial_gpt = obtener_historial_formato_gpt(sender_id) or []

            # Obtener respuesta del modelo
            respuesta = get_chat_response(user_message, contexto, historial=historial_gpt, guion=guion)

            # Enviar respuesta al usuario por WhatsApp
            try:
                send_reply(sender_id, respuesta)
            except Exception as ex:
                logging.warning(f"Fallo enviando WhatsApp: {ex}")

            # Registrar respuesta del asistente
            registrar_chat(sender_id, "asistente", respuesta)
            return func.HttpResponse("EVENT_RECEIVED", status_code=200)

        return func.HttpResponse("Método no soportado", status_code=405)

    except Exception:
        logging.exception("Error procesando la solicitud")
        return func.HttpResponse("Error", status_code=500)
