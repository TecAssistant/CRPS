
import cv2
import time
from yunet.detect_face import process_image_with_yunet
from utils.embeddings import image_to_embedding
from database.weaviate import search_by_vector
from utils.facenet import preload_image_to_embedding
import cv2
import time
import threading
import queue

from yunet.detect_face import process_image_with_yunet
from utils.facenet import preload_image_to_embedding
from database.weaviate import search_by_vector

def video_capture_threaded(model, collection):
    """
    Captura de video con OpenCV en el hilo principal y procesamiento
    (detección, embedding, búsqueda) en un hilo secundario.
    """
    # Cola de frames a procesar
    processing_queue = queue.Queue(maxsize=2)  # tamaño máximo para evitar saturar RAM
    
    # Creamos e iniciamos el hilo trabajador
    stop_event = threading.Event()
    worker = threading.Thread(
        target=processing_worker,
        args=(processing_queue, stop_event, model, collection),
        daemon=True
    )
    worker.start()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to open the camera")
        return

    cv2.namedWindow("Captured Frame", cv2.WINDOW_NORMAL)
    
    last_capture_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Unable to capture frame")
            break

        # Mostramos el frame en vivo, sin bloquear
        cv2.imshow("Captured Frame", frame)

        current_time = time.time()
        # Cada 3 segundos, encolamos un frame para procesar
        if (current_time - last_capture_time) >= 3.0:
            # Actualizamos la marca de tiempo
            last_capture_time = current_time
            
            # Copiamos el frame y lo encolamos
            frame_copy = frame.copy()
            
            # Encolamos el frame si el worker no está muy saturado
            # (Si la cola está llena, no hacemos nada para no bloquear).
            if not processing_queue.full():
                processing_queue.put(frame_copy)

        # Salir al presionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Avisamos al hilo que debe terminar
    stop_event.set()
    worker.join(timeout=2.0)  # Esperamos que termine limpio

    cap.release()
    cv2.destroyAllWindows()



def processing_worker(processing_queue, stop_event, model, collection):
    """
    Hilo de trabajo que toma frames de la cola y realiza:
      - Detección facial (YuNet).
      - Generación de embedding (FaceNet).
      - Búsqueda en Weaviate.
    """
    # Dimensiones esperadas por YuNet
    input_width, input_height = model._inputSize
    
    # Umbrales para determinar si la cara está "lo suficientemente cerca"
    min_width = 0.07 * input_width
    min_height = 0.07 * input_height
    min_area = 0.05 * (input_width * input_height)

    while not stop_event.is_set():
        try:
            # Esperamos un frame o salimos si no llega nada en 0.2s
            frame_to_process = processing_queue.get(timeout=0.2)
        except queue.Empty:
            continue  # Volvemos a comprobar si stop_event está activo

        # Realizamos la detección en este hilo
        resized_frame = cv2.resize(frame_to_process, (input_width, input_height))
        faces = model.infer(resized_frame)
        
        if faces is not None and len(faces) > 0:
            detection = faces[0]
            x, y, w, h, score = detection[:5]
            
            # Ajustamos coordenadas a int y limitamos para que no salga de rango
            x = int(max(x, 0))
            y = int(max(y, 0))
            w = int(min(w, input_width - x))
            h = int(min(h, input_height - y))

            # Checamos que la cara tenga tamaño suficiente
            area = w * h
            if w < min_width or h < min_height or area < min_area:
                print("Face too far")
            else:
                print("Face detected:", detection)
                face_img = resized_frame[y:y+h, x:x+w]
                if face_img.size > 0:
                    cropped_face, _ = process_image_with_yunet(face_img, model)
                    if cropped_face is not None and cropped_face.shape[0] > 0 and cropped_face.shape[1] > 0:
                        # Generamos embedding
                        embedding = preload_image_to_embedding(cropped_face)
                        
                        # Llamamos a Weaviate
                        # (Esta petición es lo que más tarda, pero ya no
                        #  bloquea el hilo principal)
                        search_by_vector(collection, embedding, 10)
                    else:
                        print("No se obtuvo un recorte válido de la cara.")
                else:
                    print("The face region is empty.")
        else:
            print("No face detected.")
        
        # Marcar que terminamos de procesar este item de la cola
        processing_queue.task_done()
    
    print("Worker thread stopped.")

