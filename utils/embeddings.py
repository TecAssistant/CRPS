import numpy as np
from keras.api.applications.resnet50 import ResNet50, preprocess_input
from keras.api.preprocessing import image
from utils.save_file import save_json
from PIL import Image
import json


model = ResNet50(weights="imagenet", include_top=False, pooling="avg")


def preload_image(file_name, image_path, save_path):
    img = image.load_img(
        image_path, target_size=(224, 224)
    )  # El target_size es 224, debido a que es el requerido por ResNet50
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    embedding = model.predict(x)
    embedding_list = embedding[0].tolist()
    embedding_json = json.dumps(embedding_list)
    return embedding_list
    # save_json(file_name, save_path, embedding_json)


def image_to_embedding(img_input):
    """
    Convierte una imagen (PIL Image o array de NumPy) en un embedding usando ResNet50.
    
    Args:
        img_input (PIL.Image.Image o np.ndarray): Imagen de entrada.
    
    Returns:
        list: Embedding de la imagen en forma de lista.
    """
    # Si la imagen es un array de NumPy, la convertimos a PIL Image
    if isinstance(img_input, np.ndarray):
        img_input = Image.fromarray(img_input.astype('uint8'), 'RGB')
    
    # Redimensionar la imagen a 224x224 (requerido por ResNet50)
    img_resized = img_input.resize((224, 224))
    
    # Convertir a array y expandir dimensiones
    x = image.img_to_array(img_resized)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    # Obtener el embedding
    embedding = model.predict(x)
    
    # Convertir a lista y retornar
    return embedding[0].tolist()


def generate_artificial_embedding(length):
    return np.random.rand(length).tolist()
