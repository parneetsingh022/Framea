from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt
import os

class ImageGridWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.images = self._get_images("C:\\Users\\parne\\Pictures\\Screenshots")  # Replace with your image directory

        v_layout = QVBoxLayout()
        v_layout.setSpacing(10)
        v_layout.setContentsMargins(10, 10, 10, 10)
        v_layout.addWidget(QPushButton("HELLO"), alignment=Qt.AlignTop)
        v_layout.addWidget(QLabel("HELLO"), alignment=Qt.AlignTop)
        v_layout.addWidget(QLabel("HELLO 2"), alignment=Qt.AlignTop)
        v_layout.addStretch()


        self.setLayout(v_layout)

    def _get_images(self,path : str) -> list[str]:
        # Returns a list of image paths from the given directory
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        return [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(supported_formats)]


    def on_window_resize(self, size=(0,0)):
        print("hello from image grid widget, window resized to:", size)