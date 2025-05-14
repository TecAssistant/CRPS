# utils/drive_utils.py

import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_drive(
    client_secrets_file: str = "client_secrets.json",
    credentials_file: str    = "credentials.json",
    local_port: int          = 8095
):
    gauth = GoogleAuth()
    # Le indicamos dónde está tu client_secrets y dónde guardar el token
    gauth.settings['client_config_file']    = client_secrets_file
    gauth.settings['save_credentials_file'] = credentials_file
    # Fijamos el puerto antes de arrancar el webserver
    gauth.settings['local_webserver_port']  = local_port

    # Intentamos cargar un token almacenado
    if os.path.exists(credentials_file):
        try:
            gauth.LoadCredentialsFile(credentials_file)
        except Exception:
            os.remove(credentials_file)

    # Si no hay credenciales o están inválidas, abrimos OAuth
    if not gauth.credentials or gauth.credentials.invalid:
        print(f"Abriendo navegador en http://localhost:{local_port}")
        gauth.LocalWebserverAuth()   # ya usará el puerto de settings
        gauth.SaveCredentialsFile(credentials_file)

    drive = GoogleDrive(gauth)
    print("Autenticación y token OK")
    return drive


def upload_image_to_drive(image_path, folder_id, drive=None):
    """
    Sube una imagen a Google Drive en la carpeta especificada.
    """
    if drive is None:
        drive = authenticate_drive()

    file_drive = drive.CreateFile({
        'title':   os.path.basename(image_path),
        'parents': [{'id': folder_id}]
    })
    file_drive.SetContentFile(image_path)
    try:
        file_drive.Upload()
        print(f"Imagen {os.path.basename(image_path)} subida a Google Drive.")
    finally:
        # Cerramos el handle que PyDrive2 deja abierto
        handle = getattr(file_drive, 'content', None)
        if handle:
            try:
                handle.close()
            except Exception:
                pass

