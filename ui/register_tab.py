# register_tab.py

import os
import shutil
import cv2
import threading

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
from utils.drive_utils import upload_image_to_drive


class RegisterTab(QWidget):
    """
    Pestaña de registro que:
      • Arranca un live-view guardando todos los frames en disco.
      • Al “Capture” congela un frame para previsualizar.
      • Al “Register Face” inserta el embedding en Weaviate y
        crea una subcarpeta en Drive, luego sube todos los frames
        en un hilo separado para no bloquear la UI.
    """
    def __init__(self, model, collection, drive=None,
                 drive_parent_folder_id=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.collection = collection
        self.drive = drive
        self.drive_parent_folder_id = drive_parent_folder_id

        self.local_save_dir = None     # directorio donde guardamos frames
        self.video_handler = None
        self.image_bgr = None          # último frame capturado

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ——— IZQUIERDA: Live-view + controles ———
        left = QVBoxLayout()
        self.register_image_label = QLabel("No video")
        self.register_image_label.setFixedSize(300, 300)
        self.register_image_label.setAlignment(Qt.AlignCenter)
        self.register_image_label.setStyleSheet("border:1px solid #aaa;")
        left.addWidget(self.register_image_label, alignment=Qt.AlignCenter)

        btns = QHBoxLayout()
        btn_start = QPushButton("Start Live")
        btn_start.clicked.connect(self.start_video)
        btns.addWidget(btn_start)

        btn_capture = QPushButton("Capture")
        btn_capture.clicked.connect(self.capture_image)
        btns.addWidget(btn_capture)

        btn_stop = QPushButton("Stop Live")
        btn_stop.clicked.connect(self.stop_video)
        btns.addWidget(btn_stop)

        left.addLayout(btns)

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

    # ——————————————————————————————
    # CONTROL DE VIDEO + ALMACÉN LOCAL
    # ——————————————————————————————
    def start_video(self):
        # Prepara carpeta local
        self.local_save_dir = os.path.abspath("live_capture_frames")
        if os.path.exists(self.local_save_dir):
            shutil.rmtree(self.local_save_dir)
        os.makedirs(self.local_save_dir, exist_ok=True)

        # Inicia handler pasándole el dir local
        self.video_handler = VideoRegisterHandler(
            self.register_image_label,
            save_dir=self.local_save_dir
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

        # Congela la imagen en el label
        self.image_bgr = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.register_image_label.width(),
            self.register_image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.register_image_label.setPixmap(pix)

        # Detén el feed para no seguir guardando
        self.video_handler.stop_camera()
        self.video_handler = None

    def stop_video(self):
        if self.video_handler:
            self.video_handler.stop_camera()

    # ——————————————————————————————
    # REGISTRO EN WEAVIATE + UPLOAD A DRIVE (en hilo)
    # ——————————————————————————————
    def register_user(self):
        if self.image_bgr is None:
            QMessageBox.warning(self, "Imagen faltante",
                                "Captura primero un frame para registrar.")
            return

        # 1) Insertar en Weaviate
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

        # 2) Crear carpeta en Drive: <Name>_<últimos5ID>
        last5      = props["identification"][-5:]
        folder_name = f"{props['name']}_{last5}"
        folder_meta = self.drive.CreateFile({
            'title':    folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':  [{'id': self.drive_parent_folder_id}]
        })
        folder_meta.Upload()
        new_folder_id = folder_meta['id']

        # 3) Lanzar hilo para subir los frames sin bloquear UI
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
        """
        Función que corre en background para subir cada imagen a Drive.
        """
        count = 0
        for fname in sorted(os.listdir(self.local_save_dir)):
            full_path = os.path.join(self.local_save_dir, fname)
            try:
                upload_image_to_drive(full_path, drive_folder_id, drive=self.drive)
                count += 1
            except Exception as e:
                print(f"Error subiendo {fname}: {e}")
        print(f"✅ Subida completada: {count} archivos enviados a Drive.")

