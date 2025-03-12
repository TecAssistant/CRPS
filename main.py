import weaviate
import os
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery
from utils.embeddings import preload_image, generate_artificial_embedding
from database.weaviate import (
    connect_database,
    insert_into_collection,
    print_collection,
    search_by_vector,
)
from database.collections import create_person_collection
from utils.encryption import encrypt_data, encrypt_dictionary, decrypt_dictionary
from data_handler import handler

from utils.eye_checker import process_image

test_properties = {
    "identification": 8849382934,
    "name": "Juan Gonzales",
    "age": 23,
    "role": "Teacher",
    "phone_number": "+506 39292292",
    "registration_date": "2024-05-04T00:00:00Z",
    "last_update_date": "2025-010-04T00:00:00Z",
}
# print([generate_artificial_embedding(2048) for _ in range(10)])

test_vector = generate_artificial_embedding(2048)


def test_db():
    # create_person_collection()
    # print_collection("Person")
    # newVec = preload_image("beast.json", "img/beast.jpg", "output/")
    # search_by_vector("Person", newVec, 2)
    # print_collection("Person")
    search_by_vector("Person", test_vector, 1)


def test_encryption():
    encrypted_dictionary = encrypt_dictionary(test_properties)
    print(encrypted_dictionary)
    print("-" * 40)
    decrypted_dictionary = decrypt_dictionary(encrypted_dictionary)
    print(decrypted_dictionary)


def main():
    # test_db()
    # test_encryption()
    # client = connect_database()
    # client.collections.delete("Person")
    # test_db()

    predictor_path = "shape-predictor/shape_predictor_68_face_landmarks.dat"
    image_path = "img/closed-eyes.jpg"
    eyes_open = process_image(image_path, predictor_path, ear_threshold=0.3)
    print(eyes_open)


if __name__ == "__main__":
    #dataset_path = "data_handler/dataset"
    #handler.load_dataset(dataset_path, 1)
    print(preload_image("beast.json", "img/beast.jpg", "output/"))
   # main()