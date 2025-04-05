import cv2
from database.weaviate import (
    insert_into_collection,
    print_collection,
    search_by_vector,
)
from utils.facenet import preload_image_to_embedding
from database.collections import create_person_collection
from utils.encryption import encrypt_dictionary, decrypt_dictionary

from yunet.detect_face import process_image_with_yunet
from video_recognition.video_recognition import video_capture_threaded
from yunet.yunet import YuNet
from ui.ui import MainWindow
import sys

from PyQt5 import QtWidgets

dataset_path = "data_handler/dataset"
predictor_path = "shape-predictor/shape_predictor_68_face_landmarks.dat"
yunet_path = "yunet/model/face_detection_yunet_2023mar.onnx"
collection = "Person"
test_properties = {
    "identification": 208580617,
    "name": "Isaac Ramirez",
    "age": 20,
    "role": "Student",
    "phone_number": "+506 39292292",
    "registration_date": "2024-05-04T00:00:00Z",
    "last_update_date": "2025-010-04T00:00:00Z",
}

face_detector = YuNet(modelPath=yunet_path, inputSize=[320, 320], confThreshold=0.6, nmsThreshold=0.3)

def initialize_dlib():
    # detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor(predictor_path)
    pass


def database():

    # Create a collection
    create_person_collection()

    # Remove a collection

    # client.collections.delete("Person")

    # Print a collection
    print_collection(collection)

    # Create user on weaviate
    create_user_weaviate(face_detector)

    # Search by vector
    vector = {}
    search_by_vector(collection, vector, 1)


    
def create_user_weaviate(face_detector):
    image_path = "img/Isaac.png" # image of the person you're going to insert
    user = cv2.imread(image_path)
    cropped_face, bbox_face = process_image_with_yunet(user, face_detector)

    # if cropped_face is not None:
    #     cv2.imshow("Cropped Face", cropped_face) # Muestra la imagen en una ventana llamada "Cropped Face"
    #     cv2.waitKey(0) # Espera hasta que presiones una tecla
    #     cv2.destroyAllWindows() # Cierra todas las ventanas abiertas por OpenCV

    # embedding_img = image_to_embedding(cropped_face)


    embedding_img = preload_image_to_embedding(cropped_face)
    insert_into_collection(collection,embedding_img, test_properties)

    # Test if the vector is inserted
    search_by_vector(collection, embedding_img, 10)


def test_encryption():
    encrypted_dictionary = encrypt_dictionary(test_properties)
    decrypted_dictionary = decrypt_dictionary(encrypted_dictionary)


def video(model):
    video_capture_threaded(model, collection)


def main():
    # video(face_detector)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(model=face_detector, collection=collection)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
