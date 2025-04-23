# register_tab.py
import os
import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFormLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from .ui_video_register import VideoRegisterHandler

from yunet.detect_face import process_image_with_yunet
from utils.facenet import preload_image_to_embedding
from database.weaviate import insert_into_collection, search_by_vector

class RegisterTab(QWidget):
    """
    Pestaña de registro que muestra feed en vivo y permite capturar un frame
    para luego procesarlo con FaceNet + YuNet y registrar en Weaviate.
    """
    def __init__(self, model, collection, drive=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.collection = collection
        self.drive = drive

        self.image_bgr = None                # frame capturado
        self.video_handler = None            # instancia de VideoRegisterHandler

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ------------------------
        # IZQUIERDA: Video & Botones
        # ------------------------
        left = QVBoxLayout()

        # Label donde se mostrará el feed y luego la imagen congelada
        self.register_image_label = QLabel("No video")
        self.register_image_label.setAlignment(Qt.AlignCenter)
        self.register_image_label.setFixedSize(300, 300)
        self.register_image_label.setStyleSheet("border: 1px solid #aaa;")
        left.addWidget(self.register_image_label, alignment=Qt.AlignCenter)

        # Botones de control de cámara
        btn_layout = QHBoxLayout()

        btn_start = QPushButton("Start Live")
        btn_start.clicked.connect(self.start_video)
        btn_layout.addWidget(btn_start)

        btn_capture = QPushButton("Capture")
        btn_capture.clicked.connect(self.capture_image)
        btn_layout.addWidget(btn_capture)

        btn_stop = QPushButton("Stop Live")
        btn_stop.clicked.connect(self.stop_video)
        btn_layout.addWidget(btn_stop)

        left.addLayout(btn_layout)

        # Botón para registrar en Weaviate
        btn_register = QPushButton("Register Face")
        btn_register.clicked.connect(self.register_user)
        left.addWidget(btn_register, alignment=Qt.AlignCenter)

        # ------------------------
        # DERECHA: Formulario de datos
        # ------------------------
        right = QVBoxLayout()
        form = QFormLayout()
        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.role_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.age_input = QLineEdit()

        form.addRow("Identification:", self.id_input)
        form.addRow("Name:", self.name_input)
        form.addRow("Role:", self.role_input)
        form.addRow("Phone Number:", self.phone_input)
        form.addRow("Age:", self.age_input)
        right.addLayout(form)

        main_layout.addLayout(left)
        main_layout.addLayout(right)
        self.setLayout(main_layout)

    # ------------------------
    # CONTROL DE VIDEO
    # ------------------------
    def start_video(self):
        if not self.video_handler:
            self.video_handler = VideoRegisterHandler(self.register_image_label)
        self.video_handler.start_camera()

    def capture_image(self):
        if not self.video_handler:
            QMessageBox.warning(self, "Error", "Inicia primero la cámara.")
            return

        frame = self.video_handler.capture_frame()
        if frame is None:
            QMessageBox.warning(self, "Error", "No hay frame disponible aún.")
            return

        # Congelamos la imagen en el label
        self.image_bgr = frame
        # Convertir BGR→RGB y mostrar
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_line = ch * w
        img = QImage(rgb.data, w, h, bytes_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.register_image_label.width(),
            self.register_image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.register_image_label.setPixmap(pix)

        # (opcional) parar el feed
        self.video_handler.stop_camera()

    def stop_video(self):
        if self.video_handler:
            self.video_handler.stop_camera()

    # ------------------------
    # REGISTRAR EN WEAVIATE
    # ------------------------
    def register_user(self):
        if self.image_bgr is None:
            QMessageBox.warning(self, "Imagen faltante",
                                "Por favor captura una imagen antes de registrar.")
            return

        props = {
            "identification": self.id_input.text().strip(),
            "name":           self.name_input.text().strip(),
            "role":           self.role_input.text().strip(),
            "phone_number":   self.phone_input.text().strip(),
            "age":            self.age_input.text().strip()
        }

        # Procesa y sube a Weaviate
        cropped_face, _ = process_image_with_yunet(self.image_bgr, self.model)
        if cropped_face is None:
            QMessageBox.warning(self, "Error",
                                "No se detectó cara en la imagen.")
            return

        embedding = preload_image_to_embedding(cropped_face)
        insert_into_collection(self.collection, embedding, props)
        # prueba de búsqueda opcional
        search_by_vector(self.collection, embedding, limit=5)

        QMessageBox.information(self, "Registro exitoso",
                                "¡El usuario ha sido registrado correctamente!")

