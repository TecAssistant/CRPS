import os
from utils.embeddings import preload_image

dataset_path = "/data_handler/dataset"

def generate_properties(name):
    test_properties = {
        "identification": 8849382934,
        "name": name,
        "age": 23,
        "role": "Teacher",
        "phone_number": "+506 39292292",
        "registration_date": "2024-05-04T00:00:00Z",
        "last_update_date": "2025-010-04T00:00:00Z",
    }
    return test_properties

def load_dataset(path, limit):
    images_loaded = 0
    # for imagen en dataset (mientras la cantidad no haya supeado limit)
    # obtener el filename de la imagen
    # generate_properties(filename)
    # preload_image(image_path=filename)

    for filename in os.listdir(path):
        if filename.endswith(".jpg"):
            properties = generate_properties(filename)

            image_path = os.path.join(path, filename)
            embeddings = preload_image("beast.json", image_path, "output/",)
            images_loaded += 1

            if images_loaded >= limit:
                print(properties, embeddings)
                break                