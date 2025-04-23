# ui_video_register.py
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoRegisterHandler:
    """
    Muestra un feed de cámara en vivo en un QLabel y permite capturar el frame actual.
    """
    def __init__(self, display_label, width=640, height=480, fps=30):
        self.display_label = display_label
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.width = width
        self.height = height
        self.fps = fps
        self.last_frame = None

    def start_camera(self):
        if self.cap and self.cap.isOpened():
            return
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.timer.start(int(1000 / self.fps))

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.last_frame = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.display_label.width(),
            self.display_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.display_label.setPixmap(pixmap)

    def capture_frame(self):
        """
        Devuelve una copia del último frame capturado o None si aún no hay ninguno.
        """
        return self.last_frame.copy() if self.last_frame is not None else None

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

