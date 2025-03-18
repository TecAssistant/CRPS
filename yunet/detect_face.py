import cv2 as cv
from yunet.yunet import YuNet

def process_image_with_yunet(image, model, output_path=None):
    """
    Processes an image using YuNet to detect a face, crop it, and draw its bounding box.
    
    Parameters:
      - image: Input image (already captured and processed from video_capture).
      - model: An instance of YuNet.
      - output_path: (Optional) Path to save the image with the bounding box drawn.
      
    Returns:
      - cropped_face: Cropped image of the detected face.
      - image_with_bbox: Original image with the bounding box drawn.
    """
    # Convert to grayscale and equalize histogram
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    equalized_img = cv.equalizeHist(gray)

    # Convert back to BGR if your detector expects 3 channels
    processed_image = cv.cvtColor(equalized_img, cv.COLOR_GRAY2BGR)
    
    orig_h, orig_w = processed_image.shape[:2]
    
    # Use the model's input size (e.g., 320x320)
    input_size = model._inputSize  
    
    # Resize image for detection to match expected input_size (320x320)
    detection_width, detection_height = input_size
    resized_image = cv.resize(processed_image, (detection_width, detection_height))
    
    # Run inference on the resized image
    detections = model.infer(resized_image)
    
    if detections is None or len(detections) == 0:
        raise ValueError("No face was detected in the image.")
    
    # Use the first detection (typically the highest scoring)
    bbox = detections[0][:4]  # [x, y, w, h] in detection scale (320x320)
    
    # Scale bounding box coordinates to original image size
    scale_x = orig_w / detection_width
    scale_y = orig_h / detection_height
    x = int(bbox[0] * scale_x)
    y = int(bbox[1] * scale_y)
    w = int(bbox[2] * scale_x)
    h = int(bbox[3] * scale_y)
    
    # Crop the detected face from the original image
    cropped_face = processed_image[y:y+h, x:x+w].copy()
    
    # Draw the bounding box on the original image
    image_with_bbox = processed_image.copy()
    cv.rectangle(image_with_bbox, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Save the image with the bounding box only if an output path is provided
    if output_path is not None:
        cv.imwrite(output_path, image_with_bbox)
    
    return cropped_face, image_with_bbox

