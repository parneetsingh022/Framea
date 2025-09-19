import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
)
from PySide6.QtCore import Qt
from widgets.image_grid_widget import ImageGridScrollArea
from PySide6.QtGui import QResizeEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Framea")
        self.resize(800,600)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.image_grid_scroll = ImageGridScrollArea()
        layout.addWidget(self.image_grid_scroll)
        self.setCentralWidget(central_widget)

    def resizeEvent(self, event: QResizeEvent):
        new_size = event.size()
        # Forward size to inner grid through scroll area
        self.image_grid_scroll.grid.on_window_resize(new_size)
        super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
