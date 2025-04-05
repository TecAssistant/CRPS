import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFileDialog, QFormLayout, QLineEdit,
    QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

# Ajusta estos imports a tu estructura real
from yunet.detect_face import process_image_with_yunet
from utils.facenet import preload_image_to_embedding
from database.weaviate import insert_into_collection, search_by_vector

# -------------------------------------------------------------------
#   Manejador de cámara (simple)
# -------------------------------------------------------------------
class CameraHandler:
    def __init__(self):
        self.cap = None

    def start_camera(self):
        """Inicia la captura de la cámara (usando la webcam por defecto)."""
        self.cap = cv2.VideoCapture(0)  # Índice 0 para la webcam principal
        if not self.cap.isOpened():
            print("No se pudo abrir la cámara.")

    def take_photo(self):
        """Toma una foto y retorna el frame capturado (BGR)."""
        if not self.cap or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def release_camera(self):
        """Libera la cámara."""
        if self.cap and self.cap.isOpened():
            self.cap.release()


# -------------------------------------------------------------------
#   Función para crear/inserción en Weaviate
# -------------------------------------------------------------------
def create_user_weaviate(collection, image_bgr, face_detector, user_properties):
    """
    Procesa image_bgr con YuNet, extrae embedding con FaceNet
    e inserta en Weaviate, usando los datos de user_properties.
    """
    cropped_face, bbox_face = process_image_with_yunet(image_bgr, face_detector)
    if cropped_face is None:
        print("No face found or invalid face crop.")
        return

    # Genera embedding
    embedding_img = preload_image_to_embedding(cropped_face)

    # Inserta en Weaviate (user_properties son los campos que el usuario llenó)
    insert_into_collection(collection, embedding_img, user_properties)
    print("Inserted into Weaviate with properties:", user_properties)

    # Test de búsqueda (opcional)
    search_by_vector(collection, embedding_img, limit=10)


# -------------------------------------------------------------------
#   Pestaña de registro
# -------------------------------------------------------------------
class RegisterTab(QWidget):
    """
    Pestaña de registro. Permite:
      - Subir una imagen o tomar foto (si la cámara está corriendo).
      - Llenar un formulario con datos del usuario.
      - Registrar el usuario en la base (create_user_weaviate).
    """
    def __init__(self, model, collection, camera_handler=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.collection = collection
        self.camera_handler = camera_handler  # Para "Take Photo" si la cámara está activa
        self.image_bgr = None  # Guardará la imagen a registrar

        self.init_ui()

    def init_ui(self):
        """
        Reorganiza la interfaz:
          - Izquierda: Label para la imagen, debajo los botones (Browse, Take Photo, Register).
          - Derecha: Formulario (identification, name, role, phone_number, age).
        """
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)

        # ------------------------------------------------------------------
        # COLUMNA IZQUIERDA: Imagen + Botones
        # ------------------------------------------------------------------
        left_section = QVBoxLayout()

        # Imagen / Label
        self.register_image_label = QLabel("No image selected")
        self.register_image_label.setStyleSheet("border: 1px solid #aaa;")
        self.register_image_label.setFixedSize(300, 300)
        self.register_image_label.setAlignment(Qt.AlignCenter)
        left_section.addWidget(self.register_image_label, alignment=Qt.AlignCenter)

        # Botones: "Browse Image" y "Take Photo"
        buttons_layout = QHBoxLayout()
        btn_browse = QPushButton("Browse Image")
        btn_browse.clicked.connect(self.browse_image)
        buttons_layout.addWidget(btn_browse)

        btn_take_photo = QPushButton("Take Photo")
        btn_take_photo.clicked.connect(self.take_photo)
        buttons_layout.addWidget(btn_take_photo)

        left_section.addLayout(buttons_layout)

        # Botón "Register Face"
        btn_register = QPushButton("Register Face")
        btn_register.clicked.connect(self.register_user)
        left_section.addWidget(btn_register, alignment=Qt.AlignCenter)

        # ------------------------------------------------------------------
        # COLUMNA DERECHA: Formulario de datos del usuario
        # ------------------------------------------------------------------
        right_section = QVBoxLayout()

        form_layout = QFormLayout()
        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.role_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.age_input = QLineEdit()

        form_layout.addRow("Identification:", self.id_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Role:", self.role_input)
        form_layout.addRow("Phone Number:", self.phone_input)
        form_layout.addRow("Age:", self.age_input)

        right_section.addLayout(form_layout)

        # Agregamos las dos columnas al layout principal
        main_layout.addLayout(left_section)
        main_layout.addLayout(right_section)

        # Asignamos el layout al widget
        self.setLayout(main_layout)

    # ------------------------------------------------------------------
    #   MÉTODOS PARA CARGAR/TOMAR IMAGEN
    # ------------------------------------------------------------------
    def browse_image(self):
        """Seleccionar imagen desde el disco."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return

        bgr_img = cv2.imread(file_path)
        if bgr_img is None:
            print("Error loading image.")
            return

        self.image_bgr = bgr_img
        self.display_image_in_label(bgr_img)

    def take_photo(self):
        """
        Toma una foto usando la cámara. Si el camera_handler no existe o
        la cámara no está iniciada, se inicia automáticamente.
        """
        if not self.camera_handler:
            self.camera_handler = CameraHandler()
            self.camera_handler.start_camera()

        # Verifica que la cámara esté abierta
        if not self.camera_handler.cap or not self.camera_handler.cap.isOpened():
            print("No se pudo acceder a la cámara.")
            return

        # Toma la foto
        frame = self.camera_handler.take_photo()
        if frame is None:
            print("No se pudo capturar el frame.")
            return

        self.image_bgr = frame.copy()
        self.display_image_in_label(self.image_bgr)

    def display_image_in_label(self, bgr_img):
        """Muestra la imagen en self.register_image_label."""
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        scaled_pix = pixmap.scaled(
            self.register_image_label.width(),
            self.register_image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.register_image_label.setPixmap(scaled_pix)
        self.register_image_label.setText("")  # Remueve el texto placeholder

    # ------------------------------------------------------------------
    #   REGISTRAR USUARIO
    # ------------------------------------------------------------------
    def register_user(self):
        """
        Toma la imagen (self.image_bgr) y los datos del formulario,
        e inserta todo en Weaviate.
        """
        # 1) Verificar que haya una imagen
        if self.image_bgr is None:
            QMessageBox.warning(
                self,
                "Imagen faltante",
                "Por favor, sube o toma una foto antes de registrar."
            )
            return

        # 2) Obtener datos del formulario
        user_props = {
            "identification": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "role": self.role_input.text().strip(),
            "phone_number": self.phone_input.text().strip(),
            "age": self.age_input.text().strip()
        }

        # 3) Validar que todos los campos estén completos
        if any(value == "" for value in user_props.values()):
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Por favor, llena todos los campos antes de registrar."
            )
            return

        # 4) Si todo está correcto, crear el usuario en Weaviate
        create_user_weaviate(
            collection=self.collection,
            image_bgr=self.image_bgr,
            face_detector=self.model,
            user_properties=user_props
        )
        print("Registration done.")

        # Opcional: Mensaje de éxito
        QMessageBox.information(
            self,
            "Registro exitoso",
            "¡El usuario ha sido registrado correctamente!"
        )

