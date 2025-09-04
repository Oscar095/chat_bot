from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os
import pandas as pd
from io import BytesIO
import json
import io
from pypdf import PdfReader

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Inicializar cliente global
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def registrar_chat(usuario, rol, mensaje):
    try:
        container_name = "chat-history"
        blob_name = f"{usuario}/conversacion.json"
    
        container_client = blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
        except:
            pass  # Ya existe

        blob_client = container_client.get_blob_client(blob_name)

        # Leer historial si existe
        if blob_client.exists():
            contenido_actual = blob_client.download_blob().readall().decode("utf-8")
            historial = json.loads(contenido_actual)
        else:
            historial = []

        # Agregar nuevo mensaje
        historial.append({
            "fecha": datetime.utcnow().isoformat(),
            "rol": rol,
            "mensaje": mensaje
        })

        # Subir el nuevo historial
        blob_client.upload_blob(json.dumps(historial, indent=2), overwrite=True)

    except Exception as e:
        print(f"❌ Error al registrar conversación: {e}")

def leer_archivo_blob(container_name, blob_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        contenido = blob_client.download_blob().readall().decode("utf-8")
        return contenido
    except Exception as e:
        print(f"Error leyendo {blob_name} desde {container_name}: {e}")
        return None
    
def leer_excel_blob(container_name, blob_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()
        excel_data = pd.read_excel(BytesIO(blob_data))
        return excel_data
    except Exception as e:
        print(f"Error leyendo Excel {blob_name} desde {container_name}: {e}")
        return None

def listar_archivos_blob(container_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        return [blob.name for blob in container_client.list_blobs()]
    except Exception as e:
        print(f"Error listando archivos en {container_name}: {e}")
        return []

def obtener_historial_formato_gpt(usuario):
    try:
        container_name = "chat-history"
        blob_name = f"{usuario}/conversacion.json"
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        if not blob_client.exists():
            return []

        contenido = blob_client.download_blob().readall().decode("utf-8")
        historial_raw = json.loads(contenido)

        mensajes_gpt = []
        for item in historial_raw:
            mensajes_gpt.append({
                "role": "user" if item["rol"] == "usuario" else "assistant",
                "content": item["mensaje"]
            })

        return mensajes_gpt

    except Exception as e:
        print(f"❌ Error cargando historial para {usuario}: {e}")
        return []

def leer_pdf_blob(contenedor: str, blob_nombre: str) -> str:
    """
    Lee un PDF desde Azure Blob Storage y retorna su texto.
    Requiere la variable de entorno AZURE_STORAGE_CONNECTION_STRING.
    """
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("Falta AZURE_STORAGE_CONNECTION_STRING en variables de entorno.")
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service.get_blob_client(container=contenedor, blob=blob_nombre)
    data = blob_client.download_blob().readall()
    with io.BytesIO(data) as stream:
        reader = PdfReader(stream)
        texto = []
        for page in reader.pages:
            texto.append(page.extract_text() or "")
    return "\n".join(texto)
