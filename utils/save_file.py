import json
import os

def save_json(file_name, path, content):
    """
    Guarda el contenido en un archivo JSON en la ruta especificada.

    Parámetros:
        file_name (str): Nombre del archivo (por ejemplo, "archivo.json").
        path (str): Ruta del directorio donde se guardará el archivo.
        content (str): Cadena en formato JSON que se guardará en el archivo.
                       Si prefieres trabajar con objetos Python, puedes modificar la función para usar json.dump directamente.
    """
    try:
        # Crear el directorio si no existe
        if not os.path.exists(path):
            os.makedirs(path)

        # Construir la ruta completa del archivo
        file_path = os.path.join(path, file_name)

        # Guardar el contenido en el archivo JSON
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Archivo guardado exitosamente en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
