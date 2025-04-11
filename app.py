import streamlit as st
import json
import io
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="Uploader Drive", layout="centered")
st.title("📤 Subir archivo a Google Drive desde Streamlit Cloud")

# Obtener las credenciales desde secrets
client_info = {
    "web": {
        "client_id": st.secrets["gdrive"]["client_id"],
        "client_secret": st.secrets["gdrive"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
}

SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow = Flow.from_client_config(client_info, scopes=SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')

auth_url, _ = flow.authorization_url(prompt='consent')

st.info("🔐 Haz clic en el siguiente enlace para autorizar el acceso a tu Google Drive:")
st.markdown(f"[Autorizar en Google]({auth_url})")

code = st.text_input("Pega aquí el código de autorización:")

if code:
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        service = build("drive", "v3", credentials=creds)

        # Crear carpeta si no existe
        def buscar_o_crear_carpeta(service, nombre_carpeta):
            response = service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and name='{nombre_carpeta}' and trashed=false",
                spaces='drive',
                fields='files(id, name)').execute()
            items = response.get('files', [])
            if items:
                return items[0]['id']
            else:
                file_metadata = {
                    'name': nombre_carpeta,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                return folder.get('id')

        carpeta_id = buscar_o_crear_carpeta(service, "REPORTE SELFIES")

        # Crear archivo de prueba
        contenido = "Archivo subido desde Streamlit Cloud"
        archivo = io.BytesIO(contenido.encode("utf-8"))

        metadata = {
            'name': 'archivo_streamlit.txt',
            'parents': [carpeta_id]
        }

        media = MediaIoBaseUpload(archivo, mimetype='text/plain')
        archivo_subido = service.files().create(body=metadata, media_body=media, fields='id').execute()

        enlace = f"https://drive.google.com/file/d/{archivo_subido.get('id')}/view"
        st.success("✅ Archivo subido correctamente.")
        st.markdown(f"[🔗 Ver archivo en Drive]({enlace})")

    except Exception as e:
        st.error(f"❌ Error al subir: {e}")
