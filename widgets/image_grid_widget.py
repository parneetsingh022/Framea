from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
)

from PySide6.QtCore import Qt, QSize
import os

class ImageGridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.size = QSize(0,0)
        self._images_per_row = 1
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

    def get_images_per_row(self, image_size : QSize, padding_h : int) -> int:
        '''
        Calculate how many images can fit in a row based on the current window size,
        image size, and horizontal padding.
            :param image_size: QSize object representing the size of each image.
            :param padding_h: Horizontal padding between images.
            :return: Number of images that can fit in a single row. 
        '''
        window_width = self.size.width()
        image_width = image_size.width()

        total_h_image_space = image_width + 2 * padding_h

        if not image_width or not window_width or total_h_image_space <= 0:
            return 1
        
        # Each image takes up image_width + 2 * padding_h horizontally
        images_per_row = max(1, window_width // total_h_image_space)
        return images_per_row

    def on_window_resize(self, size : QSize):
        self.size = size
        self._images_per_row = self.get_images_per_row(QSize(200,200), 10)
        print(f"Resized to: {size}, images per row: {self._images_per_row}")