import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate_drive():
    gauth = GoogleAuth()
    
    # Intenta cargar credenciales guardadas previamente
    cred_path = "credentials.json"
    if os.path.exists(cred_path):
        gauth.LoadCredentialsFile(cred_path)
    
    # Si no existe o es inválido, se realiza el flujo de autenticación
    if not gauth.credentials or gauth.credentials.invalid:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(cred_path)
    
    drive = GoogleDrive(gauth)
    return drive


def upload_image_to_drive(image_path, folder_id, drive=None):
    """
    Sube una imagen a Google Drive en la carpeta especificada.
    """
    if drive is None:
        drive = authenticate_drive()
    
    file_drive = drive.CreateFile({
        'title': os.path.basename(image_path),
        'parents': [{'id': folder_id}]
    })
    file_drive.SetContentFile(image_path)
    file_drive.Upload()
    print(f"Imagen {os.path.basename(image_path)} subida a Google Drive.")
