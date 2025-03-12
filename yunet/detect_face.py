import cv2 as cv
from yunet.yunet import YuNet

def process_image_with_yunet(image_path, output_path, model_path, input_size=[320, 320],
                             confThreshold=0.6, nmsThreshold=0.3, topK=5000,
                             backendId=0, targetId=0):
    """
    Processes an image using YuNet to detect a face, crop it, and draw its bounding box.
    
    Parameters:
      - image_path: Path to the input image.
      - output_path: Path to save the image with the bounding box drawn.
      - model_path: Path to the YuNet model.
      - input_size: Input size for the detector (list or tuple [width, height]).
      - confThreshold: Confidence threshold for detection.
      - nmsThreshold: Non-maximum suppression threshold.
      - topK: Maximum number of candidates.
      - backendId: Backend ID for OpenCV.
      - targetId: Target device ID.
      
    Returns:
      - cropped_face: Cropped image of the detected face.
      - image_with_bbox: Original image with the bounding box drawn.
    """
    # Load the original image
    image = cv.imread(image_path)
    if image is None:
        raise ValueError("Unable to load the image from the provided path.")

    # Convert to grayscale and equalize histogram
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # equalized_img = cv.equalizeHist(gray)

    # Convert back to BGR if your detector expects 3 channels
    # image = cv.cvtColor(equalized_img, cv.COLOR_GRAY2BGR)
    image = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
    
    orig_h, orig_w = image.shape[:2]
    
    # Create YuNet instance
    detector = YuNet(modelPath=model_path, inputSize=input_size, confThreshold=confThreshold, 
                     nmsThreshold=nmsThreshold, topK=topK, backendId=backendId, targetId=targetId)
    
    # Resize image for detection to match expected input_size (320x320)
    detection_width, detection_height = input_size
    resized_image = cv.resize(image, (detection_width, detection_height))
    
    # Run inference on the resized image
    detections = detector.infer(resized_image)
    
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
    cropped_face = image[y:y+h, x:x+w].copy()
    
    # Draw the bounding box on the original image
    image_with_bbox = image.copy()
    cv.rectangle(image_with_bbox, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Save the image with the bounding box

    cv.imwrite(output_path, cropped_face) # If required, can change the cropped_face to image_with_bbox
    
    return cropped_face, image_with_bbox

