import time
import queue
import threading
import cv2

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

# Ajusta estos imports según tu estructura
from yunet.detect_face import process_image_with_yunet
from utils.facenet import preload_image_to_embedding
from database.weaviate import search_by_vector


def processing_worker(processing_queue, stop_event, model, collection, result_queue):
    """
    Hilo de trabajo que toma frames de la cola y realiza:
      - Detección facial (YuNet).
      - Generación de embedding (FaceNet).
      - Búsqueda en Weaviate (search_by_vector).
    Cuando encuentra un resultado (primer usuario), lo pone en 'result_queue'.
    """
    input_width, input_height = model._inputSize

    min_width = 0.07 * input_width
    min_height = 0.07 * input_height
    min_area = 0.05 * (input_width * input_height)

    while not stop_event.is_set():
        try:
            frame_to_process = processing_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        resized_frame = cv2.resize(frame_to_process, (input_width, input_height))
        faces = model.infer(resized_frame)

        if faces is not None and len(faces) > 0:
            detection = faces[0]
            x, y, w, h, score = detection[:5]

            x = int(max(x, 0))
            y = int(max(y, 0))
            w = int(min(w, input_width - x))
            h = int(min(h, input_height - y))

            area = w * h
            if w < min_width or h < min_height or area < min_area:
                print("Face too far")
            else:
                face_img = resized_frame[y:y+h, x:x+w]
                if face_img.size > 0:
                    cropped_face, _ = process_image_with_yunet(face_img, model)
                    if (cropped_face is not None and
                            cropped_face.shape[0] > 0 and
                            cropped_face.shape[1] > 0):
                        embedding = preload_image_to_embedding(cropped_face)
                        # Llamamos a Weaviate y obtenemos el dict con user_data
                        user_data = search_by_vector(collection, embedding, 10)
                        # Si hay resultado, lo metemos a result_queue
                        if user_data:
                            result_queue.put(user_data)
                    else:
                        print("No se obtuvo un recorte válido de la cara.")
                else:
                    print("The face region is empty.")
        else:
            print("No face detected.")

        processing_queue.task_done()

    print("Worker thread stopped.")


class CameraHandler:
    def __init__(self, model, collection, camera_label, enqueue_interval=3.0):
        self.model = model
        self.collection = collection
        self.camera_label = camera_label

        # Control de cámara
        self.cap = None

        # Intervalo para encolar frames
        self.enqueue_interval = enqueue_interval
        self.last_capture_time = time.time()

        # Cola de procesamiento y de resultados
        self.processing_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue()

        self.stop_event = threading.Event()
        self.worker_thread = None

        self.timer = None
        # Timer adicional para leer la result_queue
        self.result_timer = None

        # Callback que definiremos en la ventana para reaccionar a nuevos datos
        self.on_new_user_data = None

    def start_camera(self):
        if self.cap and self.cap.isOpened():
            print("La cámara ya está activa.")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("No se pudo abrir la cámara.")
            return

        # Ajusta a la resolución que deseas, para evitar zoom excesivo
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Iniciamos el hilo de procesamiento
        if not self.worker_thread or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(
                target=processing_worker,
                args=(self.processing_queue, self.stop_event,
                      self.model, self.collection, self.result_queue),
                daemon=True
            )
            self.worker_thread.start()

        # Timer para actualizar frames de la cámara
        if not self.timer:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # ~ 33 fps

        # Timer para chequear la cola de resultados
        if not self.result_timer:
            self.result_timer = QTimer()
            self.result_timer.timeout.connect(self._check_result_queue)
            self.result_timer.start(500)  # revisa cada medio segundo

        print("Cámara iniciada.")

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Convertir a QPixmap
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # Mostrar en la etiqueta
        self.camera_label.setPixmap(pixmap)

        # Encolar cada X segundos
        current_time = time.time()
        if (current_time - self.last_capture_time) >= self.enqueue_interval:
            self.last_capture_time = current_time
            if not self.processing_queue.full():
                self.processing_queue.put(frame.copy())

    def _check_result_queue(self):
        """
        Se llama periódicamente para leer la result_queue.
        Si hay un 'user_data', lo pasamos a 'on_new_user_data'.
        """
        try:
            while True:
                user_data = self.result_queue.get_nowait()
                if self.on_new_user_data:
                    self.on_new_user_data(user_data)
        except queue.Empty:
            pass  # No hay más datos en la cola

    def stop(self):
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

        if self.timer:
            self.timer.stop()
            self.timer = None

        if self.result_timer:
            self.result_timer.stop()
            self.result_timer = None

        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        print("Cámara detenida.")
