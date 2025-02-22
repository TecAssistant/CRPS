import numpy as np
from keras.api.applications.resnet50 import ResNet50, preprocess_input
from keras.api.preprocessing import image
from utils.save_file import save_json
import json


def preload_image(file_name, image_path, save_path):
    model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
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
