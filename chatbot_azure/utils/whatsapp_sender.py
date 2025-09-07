import os
import requests
from typing import Optional

WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v22.0")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")  # p.ej. 798450080012878
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")  # Token de acceso de la app (Bearer)

GRAPH_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

def _auth_header() -> dict:
    if not WHATSAPP_TOKEN:
        raise RuntimeError("WHATSAPP_TOKEN no está configurado")
    return {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

def send_reply(to_phone_e164: str, message_text: str, preview_url: bool = False, timeout_s: int = 15) -> None:
    """
    Envía un mensaje de texto por WhatsApp Cloud API.
    - to_phone_e164: número del destinatario en formato E.164 sin espacios, p.ej. '573175085787'
    - message_text: texto a enviar
    """
    if not WHATSAPP_PHONE_NUMBER_ID:
        raise RuntimeError("WHATSAPP_PHONE_NUMBER_ID no está configurado")

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_e164,
        "type": "text",
        "text": {
            "preview_url": bool(preview_url),
            "body": message_text[:4096],  # límite de texto
        },
    }

    headers = {
        "Content-Type": "application/json",
        **_auth_header(),
    }

    resp = requests.post(GRAPH_URL, json=payload, headers=headers, timeout=timeout_s)
    if not resp.ok:
        # Lanza excepción con detalles para que __init__.py lo capture y registre
        try:
            details = resp.json()
        except Exception:
            details = resp.text
        raise RuntimeError(f"WhatsApp send failed: HTTP {resp.status_code} - {details}")
