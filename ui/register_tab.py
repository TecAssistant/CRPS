# register_tab.py

import os
import shutil
import cv2
import threading

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFormLayout, QLineEdit, QMessageBox,
    QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from .ui_video_register import VideoRegisterHandler
from yunet.detect_face import process_image_with_yunet
from utils.facenet import preload_image_to_embedding
from database.weaviate import insert_into_collection, search_by_vector
from utils.drive_utils import upload_image_to_drive


class RegisterTab(QWidget):
    def __init__(self, model, collection, drive=None,
                 drive_parent_folder_id=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.collection = collection
        self.drive = drive
        self.drive_parent_folder_id = drive_parent_folder_id

        self.local_save_dir = None
        self.video_handler = None
        self.image_bgr = None

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ——— IZQUIERDA: Selector de cámara + Live-view + controles ———
        left = QVBoxLayout()

        # selector de cámara
        cam_layout = QHBoxLayout()
        cam_layout.addWidget(QLabel("Camera:"))
        self.cam_selector = QComboBox()
        cam_layout.addWidget(self.cam_selector)
        left.addLayout(cam_layout)
        self._detect_cameras()

        # label de video / congelado
        self.register_image_label = QLabel("No video")
        self.register_image_label.setFixedSize(300, 300)
        self.register_image_label.setAlignment(Qt.AlignCenter)
        self.register_image_label.setStyleSheet("border:1px solid #aaa;")
        left.addWidget(self.register_image_label, alignment=Qt.AlignCenter)

        # botones de control
        btns = QHBoxLayout()
        btn_start   = QPushButton("Start Live")
        btn_capture = QPushButton("Capture")
        btn_stop    = QPushButton("Stop Live")
        btn_start.clicked.connect(self.start_video)
        btn_capture.clicked.connect(self.capture_image)
        btn_stop.clicked.connect(self.stop_video)
        btns.addWidget(btn_start)
        btns.addWidget(btn_capture)
        btns.addWidget(btn_stop)
        left.addLayout(btns)

        # botón de registro
        btn_register = QPushButton("Register Face")
        btn_register.clicked.connect(self.register_user)
        left.addWidget(btn_register, alignment=Qt.AlignCenter)

        # ——— DERECHA: Formulario de datos ———
        right = QVBoxLayout()
        form = QFormLayout()
        self.id_input    = QLineEdit()
        self.name_input  = QLineEdit()
        self.role_input  = QLineEdit()
        self.phone_input = QLineEdit()
        self.age_input   = QLineEdit()
        form.addRow("Identification:", self.id_input)
        form.addRow("Name:",          self.name_input)
        form.addRow("Role:",          self.role_input)
        form.addRow("Phone Number:",  self.phone_input)
        form.addRow("Age:",           self.age_input)
        right.addLayout(form)

        main_layout.addLayout(left)
        main_layout.addLayout(right)
        self.setLayout(main_layout)

    def _detect_cameras(self, max_index: int = 5):
        """
        Escanea índices 0..max_index-1 y añade al combo
        aquellos que respondan como dispositivos abiertos.
        """
        self.cam_selector.clear()
        found = False
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cam_selector.addItem(f"Camera {i}", i)
                cap.release()
                found = True
        if not found:
            # al menos pon la 0
            self.cam_selector.addItem("Camera 0", 0)

    # ——————————————————————————————
    # CONTROL DE VIDEO + ALMACÉN LOCAL
    # ——————————————————————————————
    def start_video(self):
        # montamos carpeta limpia
        self.local_save_dir = os.path.abspath("live_capture_frames")
        if os.path.exists(self.local_save_dir):
            shutil.rmtree(self.local_save_dir)
        os.makedirs(self.local_save_dir, exist_ok=True)

        # índice seleccionado
        cam_idx = self.cam_selector.currentData()
        self.video_handler = VideoRegisterHandler(
            self.register_image_label,
            save_dir=self.local_save_dir,
            camera_index=cam_idx
        )
        self.video_handler.start_camera()

    def capture_image(self):
        if not self.video_handler:
            QMessageBox.warning(self, "Error", "Inicia primero el live-view.")
            return
        frame = self.video_handler.capture_frame()
        if frame is None:
            QMessageBox.warning(self, "Error", "Aún no hay frame disponible.")
            return

        # congelar en label
        self.image_bgr = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix  = QPixmap.fromImage(qimg).scaled(
            self.register_image_label.width(),
            self.register_image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.register_image_label.setPixmap(pix)

        # opcional: detener la grabación de frames
        self.video_handler.stop_camera()

    def stop_video(self):
        if self.video_handler:
            self.video_handler.stop_camera()
            self.video_handler = None

    # ——————————————————————————————
    # REGISTRO EN WEAVIATE + UPLOAD A DRIVE (en hilo)
    # ——————————————————————————————
    def register_user(self):
        # detener live antes de procesar
        if self.video_handler:
            self.stop_video()

        if self.image_bgr is None:
            QMessageBox.warning(self, "Imagen faltante",
                                "Captura primero un frame para registrar.")
            return

        # 1) Weaviate
        props = {
            "identification": self.id_input.text().strip(),
            "name":           self.name_input.text().strip(),
            "role":           self.role_input.text().strip(),
            "phone_number":   self.phone_input.text().strip(),
            "age":            self.age_input.text().strip()
        }
        face, _ = process_image_with_yunet(self.image_bgr, self.model)
        if face is None:
            QMessageBox.warning(self, "Error",
                                "No se detectó cara. Intenta otra vez.")
            return
        emb = preload_image_to_embedding(face)
        insert_into_collection(self.collection, emb, props)
        search_by_vector(self.collection, emb, limit=5)

        # 2) Carpeta en Drive
        last5       = props["identification"][-5:]
        folder_name = f"{props['name']}_{last5}"
        folder_meta = self.drive.CreateFile({
            'title':    folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':  [{'id': self.drive_parent_folder_id}]
        })
        folder_meta.Upload()
        new_folder_id = folder_meta['id']

        # 3) Hilo de subida
        threading.Thread(
            target=self._upload_frames_worker,
            args=(new_folder_id,),
            daemon=True
        ).start()

        QMessageBox.information(
            self, "Registro iniciado",
            "Usuario registrado correctamente.\n"
            "La subida de imágenes se está haciendo en segundo plano."
        )

    def _upload_frames_worker(self, drive_folder_id):
        count = 0
        for fname in sorted(os.listdir(self.local_save_dir)):
            full_path = os.path.join(self.local_save_dir, fname)
            try:
                upload_image_to_drive(full_path, drive_folder_id, drive=self.drive)
                count += 1
            except Exception as e:
                print(f"Error subiendo {fname}: {e}")
        print(f"✅ Subida completada: {count} archivos enviados a Drive.")

