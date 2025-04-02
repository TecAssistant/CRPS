from keras.src.utils.image_utils import pil_image
import weaviate
import os
import dlib
import cv2
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery
from utils.embeddings import image_to_embedding, preload_image, generate_artificial_embedding
from database.weaviate import (
    connect_database,
    insert_into_collection,
    print_collection,
    search_by_vector,
)
from utils.facenet import preload_image_to_embedding
from database.collections import create_person_collection
from utils.encryption import encrypt_data, encrypt_dictionary, decrypt_dictionary
from data_handler import handler

from utils.eye_checker import process_image
from yunet.detect_face import process_image_with_yunet
from video_recognition.video_recognition import video_capture_threaded
from yunet.yunet import YuNet


predictor_path = "shape-predictor/shape_predictor_68_face_landmarks.dat"
yunet_path = "yunet/model/face_detection_yunet_2023mar.onnx"

test_properties = {
    "identification": 208580617,
    "name": "Isaac Ramirez",
    "age": 20,
    "role": "Student",
    "phone_number": "+506 39292292",
    "registration_date": "2024-05-04T00:00:00Z",
    "last_update_date": "2025-010-04T00:00:00Z",
}

collection = "Person"
# print([generate_artificial_embedding(2048) for _ in range(10)])
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

test_vector = generate_artificial_embedding(2048)


def test_db():
    # create_person_collection()
    # print_collection("Person")
    # newVec = preload_image("beast.json", "img/beast.jpg", "output/")
    # search_by_vector("Person", newVec, 2)
    # print_collection("Person")
    # newVec = preload_image("beast.json", "img/beast.jpg", "output/")
    search_by_vector(collection, test_vector, 1)


def test_encryption():
    encrypted_dictionary = encrypt_dictionary(test_properties)
    print(encrypted_dictionary)
    print("-" * 40)
    decrypted_dictionary = decrypt_dictionary(encrypted_dictionary)
    print(decrypted_dictionary)


def upload_img(face_detector):
    image_path = "img/Isaac.png"
    isaac = cv2.imread(image_path)
    cropped_face, bbox_face = process_image_with_yunet(isaac, face_detector)
    # if cropped_face is not None:
    #     cv2.imshow("Cropped Face", cropped_face)  # Muestra la imagen en una ventana llamada "Cropped Face"
    #     cv2.waitKey(0)                         # Espera hasta que presiones una tecla
    #     cv2.destroyAllWindows()                # Cierra todas las ventanas abiertas por OpenCV
    # embedding_img = image_to_embedding(cropped_face)
    embedding_img = preload_image_to_embedding(cropped_face)
    insert_into_collection(collection,embedding_img, test_properties)
    search_by_vector(collection, embedding_img, 10)

def video(model):
    video_capture_threaded(model, collection)

def check_eyes():
    pass
    # for x in range(1,10):
    #     eyes_open = process_image(image_path,detector, predictor, ear_threshold=0.3)
    #     print(eyes_open)

def main():
    # test_db()
    # test_encryption()
    # client.collections.delete("Person")
    # test_db()
    face_detector = YuNet(modelPath=yunet_path, inputSize=[320, 320], confThreshold=0.6, nmsThreshold=0.3)
    # create_person_collection()
    # upload_img(face_detector)
    video(face_detector)
    # upload_img(face_detector)

    



if __name__ == "__main__":
    dataset_path = "data_handler/dataset"
    # handler.load_dataset(dataset_path, 20)
    # handler.test_images_loaded(dataset_path, 20)
    # print(preload_image("beast.json", "img/beast.jpg", "output/"))
    # insert_into_collection("Person", adrian, test_properties)

    # search_by_vector("Person", adrian, 10)
    main()
