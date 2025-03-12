import cv2
import dlib
from imutils import face_utils
from scipy.spatial import distance as dist

def eye_aspect_ratio(eye):
    """
    Calcula el Eye Aspect Ratio (EAR) para un ojo dado.
    
    :param eye: Lista o array con 6 puntos (x, y) correspondientes a los landmarks del ojo.
    :return: EAR calculado.
    """
    # Distancias verticales
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    
    # Distancia horizontal
    C = dist.euclidean(eye[0], eye[3])
    
    # Calcular EAR
    ear = (A + B) / (2.0 * C)
    return ear

def check_closed_eye(eye_aspect_ratio) -> bool:
    """
    Verifica si el EAR es menor que el umbral definido, lo que indica que el ojo está cerrado.
    
    :param eye_aspect_ratio: Valor EAR calculado.
    :return: True si está cerrado, False en caso contrario.
    """
    eye_ar_thresh = 0.2
    return eye_aspect_ratio < eye_ar_thresh


def process_image(image_path, predictor_path, ear_threshold=0.3):
    """
    Procesa una imagen para detectar rostros, calcular el EAR para ambos ojos y determinar 
    si los ojos están abiertos o cerrados, retornando un valor booleano.
    
    :param image_path: Ruta a la imagen.
    :param predictor_path: Ruta al predictor de landmarks faciales (por ejemplo, shape_predictor_68_face_landmarks.dat).
    :param ear_threshold: Umbral de EAR por debajo del cual se considera que el ojo está cerrado.
    :return: True si los ojos están abiertos, False si están cerrados, o None si no se detecta ningún rostro.
    """
    # Inicializar el detector de rostros y el predictor de landmarks.
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    
    # Cargar la imagen y convertirla a escala de grises.
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("No se encontró la imagen o no se pudo cargar.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros en la imagen.
    rects = detector(gray, 1)
    if len(rects) == 0:
        return None  # No se detectó ningún rostro.
    
    # Procesar el primer rostro detectado.
    rect = rects[0]
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)
    
    # Extraer landmarks para los ojos.
    leftEye = shape[42:48]
    rightEye = shape[36:42]
    
    # Calcular el EAR para ambos ojos.
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    
    # Retornar True si los ojos están abiertos, False si están cerrados.
    return ear >= ear_threshold

