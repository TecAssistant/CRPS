import numpy as np
from keras_facenet import FaceNet
from keras.api.preprocessing import image
from PIL import Image


model = FaceNet()


def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm


def preload_image_faceNet(image_path):
    img = image.load_img(image_path, target_size=(160, 160))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    embedding = model.embeddings(x)
    normalized_embedding = normalize_embedding(embedding[0])

    return normalized_embedding.tolist()

def preload_image_to_embedding(image):
    # Si image ya es un arreglo, no es necesario convertirlo
    x = np.expand_dims(image, axis=0)
    embedding = model.embeddings(x)
    normalized_embedding = normalize_embedding(embedding[0])
    return normalized_embedding.tolist()


def generate_artificial_embedding(length):
    return np.random.rand(length).tolist()

