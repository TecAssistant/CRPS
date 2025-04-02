import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QGridLayout
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt  # Asegúrate de importar Qt
from PyQt5.QtGui import QGuiApplication  # Para centrar la ventana
from PyQt5 import QtCore

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejemplo de Interfaz - PyQt5")
        self.setMinimumSize(900, 500)

        # --- Widget central ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout principal (horizontal) que divide en dos secciones: izquierda (cámara) y derecha (información).
        main_layout = QHBoxLayout(central_widget)

        # ---------------------------------------------------------------------
        # SECCIÓN IZQUIERDA: CÁMARA
        # ---------------------------------------------------------------------
        left_section = QVBoxLayout()

        # Etiqueta de título de la sección (opcional)
        lbl_camera_title = QLabel("Cámara")
        lbl_camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        left_section.addWidget(lbl_camera_title)

        # Marco (Frame) para la vista previa de la cámara
        camera_frame = QFrame()
        camera_frame.setStyleSheet("background-color: #1a1a1a;")  # color oscuro
        camera_frame.setMinimumSize(400, 300)
        camera_frame.setFrameShape(QFrame.StyledPanel)
        camera_frame.setFrameShadow(QFrame.Raised)

        # Layout dentro del frame (para centrar el ícono y el texto)
        frame_layout = QVBoxLayout(camera_frame)
        frame_layout.setAlignment(Qt.AlignCenter)

        # Etiqueta con ícono de cámara (placeholder)
        camera_icon = QLabel()
        camera_icon.setAlignment(Qt.AlignCenter)
        camera_icon.setText("📷")
        camera_icon.setFont(QFont("Arial", 40))
        frame_layout.addWidget(camera_icon)

        # Etiqueta "Vista previa de la cámara"
        lbl_camera_preview = QLabel("Vista previa de la cámara")
        lbl_camera_preview.setStyleSheet("color: #cccccc;")
        lbl_camera_preview.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(lbl_camera_preview)

        left_section.addWidget(camera_frame)

        # Botón "Iniciar Cámara"
        btn_iniciar_camara = QPushButton("Iniciar Cámara")
        btn_iniciar_camara.setFixedWidth(150)
        left_section.addWidget(btn_iniciar_camara, alignment=Qt.AlignCenter)

        # Espaciador final
        left_section.addStretch()
        main_layout.addLayout(left_section)

        # ---------------------------------------------------------------------
        # SECCIÓN DERECHA: INFORMACIÓN
        # ---------------------------------------------------------------------
        right_section = QVBoxLayout()

        # Título de la sección
        lbl_info_title = QLabel("Información")
        lbl_info_title.setFont(QFont("Arial", 14, QFont.Bold))
        right_section.addWidget(lbl_info_title)

        # Grupo para agrupar la información
        info_group = QGroupBox()
        info_layout = QVBoxLayout(info_group)

        # Imagen de perfil (placeholder)
        profile_icon = QLabel()
        profile_icon.setAlignment()
        profile_icon.setText("Icono\nUsuario")
        profile_icon.setStyleSheet("border: 1px solid #ccc; border-radius: 40px;")
        profile_icon.setFixedSize(80, 80)
        info_layout.addWidget(profile_icon, alignment=Qt::AlignCenter)

        # Datos en un GridLayout
        data_layout = QGridLayout()
        
        lbl_nombre_desc = QLabel("Nombre")
        lbl_id_desc = QLabel("ID")
        lbl_depto_desc = QLabel("Departamento")
        lbl_cargo_desc = QLabel("Cargo")
        lbl_estado_desc = QLabel("Estado")

        lbl_nombre_val = QLabel("Ana García")
        lbl_id_val = QLabel("12345678")
        lbl_depto_val = QLabel("Recursos Humanos")
        lbl_cargo_val = QLabel("Gerente")

        lbl_estado_val = QLabel("Activo")
        lbl_estado_val.setStyleSheet("color: green; font-weight: bold;")

        data_layout.addWidget(lbl_nombre_desc, 0, 0)
        data_layout.addWidget(lbl_nombre_val, 0, 1)
        data_layout.addWidget(lbl_id_desc,    1, 0)
        data_layout.addWidget(lbl_id_val,     1, 1)
        data_layout.addWidget(lbl_depto_desc, 2, 0)
        data_layout.addWidget(lbl_depto_val,  2, 1)
        data_layout.addWidget(lbl_cargo_desc, 3, 0)
        data_layout.addWidget(lbl_cargo_val,  3, 1)
        data_layout.addWidget(lbl_estado_desc,4, 0)
        data_layout.addWidget(lbl_estado_val, 4, 1)

        info_layout.addLayout(data_layout)
        right_section.addWidget(info_group)

        # Espaciador final
        right_section.addStretch()
        main_layout.addLayout(right_section)

        # Ajustamos el layout principal
        central_widget.setLayout(main_layout)

        # Centrar la ventana en la pantalla
        self.centerOnScreen()

    def centerOnScreen(self):
        """
        Función auxiliar para centrar la ventana en la pantalla usando QGuiApplication.
        Si obtienes None, revisa si tu sistema tiene configurado un 'screen' correcto.
        """
        # Obtenemos la geometría de la pantalla principal
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            screen_center = screen.availableGeometry().center()
            frame_geom = self.frameGeometry()
            frame_geom.moveCenter(screen_center)
            self.move(frame_geom.topLeft())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

