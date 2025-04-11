import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import uuid

# Título de la app
st.title("Subir selfie a Google Drive")

# Crear las credenciales desde secrets.toml
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["google_service_account"]
)

# ID de la carpeta de destino en Google Drive
FOLDER_ID = "1sLt8ub1cYLKZ_TgjFRpXndcn4bY14xzY"

def subir_a_drive(archivo, nombre_archivo):
    service = build("drive", "v3", credentials=credentials)
    file_metadata = {
        "name": nombre_archivo,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(archivo, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

# Formulario para subir imagen
with st.form("subir_selfie"):
    nombre = st.text_input("Nombre completo")
    selfie = st.file_uploader("Sube tu foto tipo selfie", type=["jpg", "jpeg", "png"])
    enviar = st.form_submit_button("Subir")

if enviar and nombre and selfie:
    nombre_archivo = f"{nombre.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.jpg"
    ruta_temporal = os.path.join("temp", nombre_archivo)
    os.makedirs("temp", exist_ok=True)

    with open(ruta_temporal, "wb") as f:
        f.write(selfie.read())

    with st.spinner("Subiendo a Google Drive..."):
        archivo_id = subir_a_drive(ruta_temporal, nombre_archivo)
        st.success(f"¡Subido con éxito! ID del archivo: {archivo_id}")

    os.remove(ruta_temporal)
elif enviar:
    st.warning("Por favor completa todos los campos.")
