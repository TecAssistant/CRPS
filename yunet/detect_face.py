import cv2 as cv
from yunet.yunet import YuNet

def process_image_with_yunet(image, model, output_path=None):
    """
    Processes an image using YuNet to detect a face, crop it, and draw its bounding box.
    
    Parameters:
      - image: Input image (capturada y procesada previamente).
      - model: Instancia de YuNet.
      - output_path: (Opcional) Ruta para guardar la imagen con la caja dibujada.
      
    Returns:
      - cropped_face: Imagen recortada de la cara detectada (o None si no se detecta).
      - image_with_bbox: Imagen original con la caja dibujada (o la imagen original si falla).
    """
    try:
        # gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # equalized_img = cv.equalizeHist(gray)

        # processed_image = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)

        processed_image = image
        
        orig_h, orig_w = processed_image.shape[:2]
        
        input_size = model._inputSize  
        detection_width, detection_height = input_size
        
        resized_image = cv.resize(processed_image, (detection_width, detection_height))
        
        detections = model.infer(resized_image)
        
        if detections is None or len(detections) == 0:
            print("No se detectó ninguna cara en la imagen.")
            return None, processed_image
        
        # Seleccionar la primera detección (la de mayor score)
        bbox = detections[0][:4]  # [x, y, w, h] en escala de detección
        
        # Escalar las coordenadas del bounding box al tamaño original
        scale_x = orig_w / detection_width
        scale_y = orig_h / detection_height
        x = int(bbox[0] * scale_x)
        y = int(bbox[1] * scale_y)
        w = int(bbox[2] * scale_x)
        h = int(bbox[3] * scale_y)
        
        # Verificar que las dimensiones del crop sean válidas
        if w <= 0 or h <= 0:
            print("El recorte de la cara no es válido.")
            return None, processed_image
        
        cropped_face = processed_image[y:y+h, x:x+w].copy()
        
        image_with_bbox = processed_image.copy()
        cv.rectangle(image_with_bbox, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if output_path is not None:
            cv.imwrite(output_path, image_with_bbox)
        
        return cropped_face, image_with_bbox
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None, image


