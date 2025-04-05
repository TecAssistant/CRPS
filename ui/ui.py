# ui.py

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QGridLayout
)
from PyQt5.QtGui import QFont, QCloseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

# Importamos nuestra lógica de cámara
from .ui_video import CameraHandler


class MainWindow(QMainWindow):
    def __init__(self, model=None, collection=None):
        super().__init__()
        self.setWindowTitle("PyQt5 - Camera + Info")
        self.setMinimumSize(900, 500)

        self.camera_handler = None
        self.model = model
        self.collection = collection

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # ------------------------------------------------------------------
        # LEFT SECTION: CAMERA
        # ------------------------------------------------------------------
        left_section = QVBoxLayout()

        lbl_camera_title = QLabel("Camera")
        lbl_camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        left_section.addWidget(lbl_camera_title)

        camera_frame = QFrame()
        camera_frame.setStyleSheet("background-color: #1a1a1a;")
        camera_frame.setMinimumSize(400, 300)
        camera_frame.setFrameShape(QFrame.StyledPanel)
        camera_frame.setFrameShadow(QFrame.Raised)

        frame_layout = QVBoxLayout(camera_frame)
        frame_layout.setAlignment(Qt.AlignCenter)

        # Label to show the video
        self.camera_feed_label = QLabel()
        self.camera_feed_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_label.setText("📷")  # Placeholder
        self.camera_feed_label.setFont(QFont("Arial", 40))
        frame_layout.addWidget(self.camera_feed_label)

        lbl_camera_preview = QLabel("Camera preview")
        lbl_camera_preview.setStyleSheet("color: #cccccc;")
        lbl_camera_preview.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(lbl_camera_preview)

        left_section.addWidget(camera_frame)

        # Button to start the camera
        btn_start_camera = QPushButton("Start Camera")
        btn_start_camera.setFixedWidth(150)
        btn_start_camera.clicked.connect(self.handle_start_camera)
        left_section.addWidget(btn_start_camera, alignment=Qt.AlignCenter)

        left_section.addStretch()
        main_layout.addLayout(left_section)

        # ------------------------------------------------------------------
        # RIGHT SECTION: USER INFORMATION
        # ------------------------------------------------------------------
        right_section = QVBoxLayout()

        lbl_info_title = QLabel("Information")
        lbl_info_title.setFont(QFont("Arial", 14, QFont.Bold))
        right_section.addWidget(lbl_info_title)

        info_group = QGroupBox()
        info_layout = QVBoxLayout(info_group)

        # (placeholder) Profile icon
        profile_icon = QLabel("User\nIcon")
        profile_icon.setStyleSheet("border: 1px solid #ccc; border-radius: 40px;")
        profile_icon.setFixedSize(80, 80)
        profile_icon.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(profile_icon, alignment=Qt.AlignCenter)

        data_layout = QGridLayout()

        # Descriptive labels
        lbl_name_desc = QLabel("Name:")
        lbl_age_desc  = QLabel("Age:")
        lbl_role_desc = QLabel("Role:")
        lbl_id_desc   = QLabel("Identification:")
        lbl_state_desc= QLabel("State:")

        # Value labels (initially empty)
        self.lbl_name_val = QLabel("")
        self.lbl_age_val  = QLabel("")
        self.lbl_role_val = QLabel("")
        self.lbl_id_val   = QLabel("")
        self.lbl_state_val = QLabel("Unknown")  # default state

        # Add everything to the grid
        data_layout.addWidget(lbl_name_desc,       0, 0)
        data_layout.addWidget(self.lbl_name_val,   0, 1)
        data_layout.addWidget(lbl_age_desc,        1, 0)
        data_layout.addWidget(self.lbl_age_val,    1, 1)
        data_layout.addWidget(lbl_role_desc,       2, 0)
        data_layout.addWidget(self.lbl_role_val,   2, 1)
        data_layout.addWidget(lbl_id_desc,         3, 0)
        data_layout.addWidget(self.lbl_id_val,     3, 1)
        data_layout.addWidget(lbl_state_desc,      4, 0)
        data_layout.addWidget(self.lbl_state_val,  4, 1)

        info_layout.addLayout(data_layout)
        right_section.addWidget(info_group)

        right_section.addStretch()
        main_layout.addLayout(right_section)

        central_widget.setLayout(main_layout)
        self.centerOnScreen()

    def handle_start_camera(self):
        """Triggered when the user clicks on 'Start Camera'."""
        if not self.camera_handler:
            # Create a CameraHandler only the first time
            self.camera_handler = CameraHandler(
                model=self.model,
                collection=self.collection,
                camera_label=self.camera_feed_label,
                enqueue_interval=3.0
            )
            # Connect its 'on_new_user_data' to our local method
            self.camera_handler.on_new_user_data = self.updateUIWithUserData

        self.camera_handler.start_camera()

    def updateUIWithUserData(self, user_data):
        """
        Automatically called when the camera thread finds
        a user and puts it in the result_queue.
        """
        print("Received data from worker:", user_data)

        # Extract fields
        name = user_data.get("name", "").strip('"')
        age  = user_data.get("age", "")
        role = user_data.get("role", "").strip('"')
        identification = user_data.get("identification", "")
        confidence = user_data.get("confidence", 0)

        # Assign to labels
        self.lbl_name_val.setText(name)
        self.lbl_age_val.setText(age)
        self.lbl_role_val.setText(role)
        self.lbl_id_val.setText(identification)

        # Update "State" label based on confidence
        if confidence > 50:
            self.lbl_state_val.setText("Recognized")
            self.lbl_state_val.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_state_val.setText("Uncertain")
            self.lbl_state_val.setStyleSheet("color: red; font-weight: bold;")

    def closeEvent(self, a0: QCloseEvent):
        """Stop the camera and close properly."""
        if self.camera_handler:
            self.camera_handler.stop()
        super().closeEvent(a0)

    def centerOnScreen(self):
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            screen_center = screen.availableGeometry().center()
            frame_geom = self.frameGeometry()
            frame_geom.moveCenter(screen_center)
            self.move(frame_geom.topLeft())
