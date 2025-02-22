import numpy as np
import tensorflow as tf
from tensorflow.python import keras
from keras.api.applications.resnet50 import ResNet50, preprocess_input
from keras.api.preprocessing import image

from numpy import dot
from numpy.linalg import norm
from PIL import Image
from utils.save_file import save_json
import json
import weaviate, os
import weaviate.classes as wvc

def connect_to_client(port):
    client = weaviate.connect_to_local("localhost", 8090, 50051)
    client.is_ready()

def vector_query():
    pass

def preload_image(file_name, image_path, save_path):
    model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    img = image.load_img(image_path, target_size=(224, 224)) # El target_size es 224, debido a que es el requerido por ResNet50
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    embedding = model.predict(x)
    embedding_list = embedding[0].tolist()
    embedding_json = json.dumps(embedding_list)
    save_json(file_name, save_path, embedding_json)


def distancia_euclidiana(v1, v2):
    """
    Calcula la distancia euclidiana entre dos vectores.

    La distancia euclidiana es la longitud del segmento de línea recta
    que conecta los dos puntos en un espacio n-dimensional.
    
    Parámetros:
        v1 (array-like): Primer vector de características.
        v2 (array-like): Segundo vector de características.

    Retorna:
        float: La distancia euclidiana entre v1 y v2.
    """
    # Se resta v2 de v1 para obtener la diferencia entre ambos vectores
    diferencia = v1 - v2
    # Se calcula la norma (magnitud) de la diferencia, que representa la distancia
    distancia = np.linalg.norm(diferencia)
    return distancia

def similitud_coseno(v1, v2):
    """
    Calcula la similitud coseno entre dos vectores.

    La similitud coseno es el coseno del ángulo entre dos vectores en un espacio
    n-dimensional. Valores cercanos a 1 indican que los vectores son muy similares,
    mientras que valores cercanos a -1 indican que son opuestos.
    
    Parámetros:
        v1 (array-like): Primer vector de características.
        v2 (array-like): Segundo vector de características.

    Retorna:
        float: La similitud coseno entre v1 y v2.
    """
    # Se calcula el producto punto de los dos vectores
    producto_punto = dot(v1, v2)
    # Se calcula la norma (magnitud) de cada vector
    norma_v1 = norm(v1)
    norma_v2 = norm(v2)
    # Se calcula la similitud coseno dividiendo el producto punto por el producto de las normas
    similitud = producto_punto / (norma_v1 * norma_v2)
    return similitud



def main():
    human_path = "img/human-face.jpeg"
    path2 = "img/Selfie.png"
    port = 8090
    connect_to_client(port)

    # dest = "output"
    # # image = Image.open(path)
    # image.show()
    # preload_image("human-face.json", human_path, dest)



if __name__ == "__main__":
    main()




