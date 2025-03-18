
import cv2
import time

from yunet.detect_face import process_image_with_yunet
def video_capture(model):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se puede abrir la cámara")
        exit()

    cv2.namedWindow("Frame Capturado", cv2.WINDOW_NORMAL)
    
    last_capture_time = time.time()
    frame_to_process = None

    # Definimos el tamaño de entrada esperado
    input_width, input_height = 320, 320

    # Definimos el umbral relativo (40% de cada dimensión)
    min_width = 0.07 * input_width  # 128 píxeles
    min_height = 0.07 * input_height  # 128 píxeles

    # Umbral de área, el área del rostro debe ser al menos el 30% del total
    min_area = 0.05 * (input_width * input_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el frame")
            break

        cv2.imshow("Frame Capturado", frame)

        current_time = time.time()
        if current_time - last_capture_time >= 1:
            frame_to_process = frame.copy()  # Guarda una copia para procesarla después
            last_capture_time = current_time
            # Procesamiento acá
            
            input_size = model._inputSize  #(320, 320)
            resized_frame = cv2.resize(frame_to_process, input_size)

            faces = model.infer(resized_frame)
            if faces is not None and len(faces) > 0:
                # Logica para el analisis de bounding boxes y distancias
                detection = faces[0]
                x, y, w, h, score = detection[:5]
                area = w * h

                # Clamping de las coordenadas para que estén dentro del frame
                x = int(max(x, 0))
                y = int(max(y, 0))
                w = int(min(w, input_width - x))
                h = int(min(h, input_height - y))

                # Si el bounding box es muy pequeño, se considera que el rostro está lejos
                if w < min_width or h < min_height or (w * h) < min_area:
                    print("Rostro lejano")
                else:
                    print("Rostro detectado:", detection)
                    # Extrae la región de la imagen donde se encuentra el rostro
                    face_img = resized_frame[y:y+h, x:x+w]

                    # Implement the process image logic here
                    if face_img.size > 0:
                        # cv2.imshow("Rostro", face_img)
                        cropped_face, image_with_bbox = process_image_with_yunet(face_img, model)
                        cv2.imshow("Rostro", cropped_face)
                    else:
                        print("La región del rostro está vacía.")
            else:
                print("No se detectó ningún rostro.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

