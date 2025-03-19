
import cv2
import time
from yunet.detect_face import process_image_with_yunet
from utils.embeddings import image_to_embedding
from database.weaviate import search_by_vector
from utils.facenet import preload_image_to_embedding

def video_capture(model, collection):
    """
    Capture video from the camera, process frames in real-time, and detect faces using the provided model.

    This function opens the default camera, displays the live video feed, and every second processes
    a frame by resizing it to the expected input size of the model. It then runs face detection,
    analyzes the bounding boxes to determine if the detected face is close enough based on relative
    size thresholds, and if a valid face is detected, calls 'process_image_with_yunet' to further
    process the face image (e.g., convert to grayscale, equalize histogram, and draw a bounding box).
    The resulting cropped face is displayed in a separate window.

    Parameters:
        model: An instance of a face detection model (e.g., YuNet) that has an attribute '_inputSize'
               and a method 'infer' for performing face detection.
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Unable to open the camera")
        exit()

    cv2.namedWindow("Captured Frame", cv2.WINDOW_NORMAL)
    
    last_capture_time = time.time()
    frame_to_process = None

    # Define the expected input size
    input_width, input_height = 320, 320

    # Define relative thresholds (7% of each dimension)
    min_width = 0.07 * input_width  # ~22.4 pixels
    min_height = 0.07 * input_height  # ~22.4 pixels

    # Area threshold: face area must be at least 5% of the total area
    min_area = 0.05 * (input_width * input_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Unable to capture frame")
            break

        cv2.imshow("Captured Frame", frame)

        current_time = time.time()
        if current_time - last_capture_time >= 3:
            frame_to_process = frame.copy()  # Save a copy to process later
            last_capture_time = current_time
            # Processing here

            input_size = model._inputSize  # (320, 320)
            resized_frame = cv2.resize(frame_to_process, input_size)

            faces = model.infer(resized_frame)
            if faces is not None and len(faces) > 0:
                # Logic for analyzing bounding boxes and distances
                detection = faces[0]
                x, y, w, h, score = detection[:5]
                area = w * h

                # Clamp the coordinates to ensure they remain within the frame
                x = int(max(x, 0))
                y = int(max(y, 0))
                w = int(min(w, input_width - x))
                h = int(min(h, input_height - y))

                # If the bounding box is too small, consider the face as being too far
                if w < min_width or h < min_height or (w * h) < min_area:
                    print("Face too far")
                else:
                    print("Face detected:", detection)
                    # Extract the region of the image where the face is located
                    face_img = resized_frame[y:y+h, x:x+w]

                    # Implement the process image logic here:
                    if face_img.size > 0:
                        cropped_face, image_with_bbox = process_image_with_yunet(face_img, model)
                        if cropped_face is not None and cropped_face.shape[0] > 0 and cropped_face.shape[1] > 0:
                            # embedding = image_to_embedding(cropped_face)
                            embedding = preload_image_to_embedding(cropped_face)
                            search_by_vector(collection, embedding, 10)
                            cv2.imshow("Face", cropped_face)
                        else:
                            print("No se obtuvo un recorte válido de la cara.")
                    else:
                        print("The face region is empty.")
            else:
                print("No face detected.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

