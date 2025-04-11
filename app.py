import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

st.set_page_config(page_title="Subir Selfies a Drive", page_icon="📷")

st.title("📸 Subir archivo a Google Drive")
st.write("Carga un archivo y se subirá automáticamente a tu carpeta en Drive.")

# Configurar credenciales desde secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=["https://www.googleapis.com/auth/drive"]
)

# Crear cliente de Google Drive
service = build("drive", "v3", credentials=credentials)

# ID de la carpeta en Google Drive (proporcionado por el usuario)
FOLDER_ID = "1sLt8ub1cYLKZ_TgjFRpXndcn4bY14xzY"

# Subida de archivo
uploaded_file = st.file_uploader("Selecciona un archivo", type=None)

if uploaded_file is not None:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Crear el archivo en Google Drive
    file_metadata = {
        "name": uploaded_file.name,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(uploaded_file.name, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    st.success(f"✅ Archivo subido correctamente a Drive con ID: {file.get('id')}")

    # Limpiar archivo local
    os.remove(uploaded_file.name)
