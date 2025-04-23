# ui_video_register.py

import os
import time
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoRegisterHandler:
    """
    Muestra un feed vivo en un QLabel y va salvando cada frame en disco
    en un directorio local (save_dir) para luego subirlo a Drive.
    Ahora acepta selección de índice de cámara.
    """
    def __init__(self,
                 display_label,
                 save_dir=None,
                 camera_index: int = 0,
                 width: int = 640,
                 height: int = 480,
                 fps: int = 30):
        self.display_label = display_label
        self.save_dir = save_dir
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.last_frame = None

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            # limpiar cualquier imagen previa
            for f in os.listdir(save_dir):
                os.remove(os.path.join(save_dir, f))

    def start_camera(self):
        if self.cap and self.cap.isOpened():
            return
        # usa el índice seleccionado
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.timer.start(int(1000 / self.fps))

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        self.last_frame = frame
        # mostrar en QLabel
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.display_label.width(),
            self.display_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.display_label.setPixmap(pix)

        # guardar en disco
        if self.save_dir:
            ts = int(time.time() * 1000)
            cv2.imwrite(os.path.join(self.save_dir, f"frame_{ts}.jpg"), frame)

    def capture_frame(self):
        return self.last_frame.copy() if self.last_frame is not None else None

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

