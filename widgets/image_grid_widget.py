from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QGridLayout, QScrollArea, QSizePolicy
)

from PySide6.QtGui import QPixmap, QCursor

from PySide6.QtCore import Qt, QSize
import os

class ImageCard(QWidget):
    def __init__(self, image_path: str, image_size: QSize = QSize(200,200), padding: int = 10):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(0)

        image = QPixmap(image_path)
        image = self._get_scalled_pixmap(image, image_size)
        image_label = QLabel()
        image_label.setPixmap(image)
        image_label.setFixedSize(image_size)  # prevent vertical stretch
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setCursor(QCursor(Qt.PointingHandCursor))  # Set cursor
        layout.addWidget(image_label)

        self.setLayout(layout)
        # Do not allow the card to expand vertically; keep a tight size hint
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def _get_scalled_pixmap(self, pixmap : QPixmap, size : QSize) -> QPixmap:
        # Scale and crop the pixmap to be square
        scaled_pixmap = pixmap.scaled(size.width(), size.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        rect = scaled_pixmap.rect()
        x = (rect.width() - size.width()) // 2
        y = (rect.height() - size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x, y, size.width(), size.height())
        return cropped_pixmap

class ImageGridWidget(QWidget):
    def __init__(self, image_size: QSize = QSize(200,200), padding: int = 10):
        super().__init__()
        self.image_size = image_size
        self.padding = padding
        self._images_per_row = 1
        # TODO: make image directory configurable / injectable
        self.image_paths = self._get_images("C:\\Users\\parne\\Pictures\\Screenshots")  # Replace with your image directory

        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(padding)
        self.grid_layout.setVerticalSpacing(padding)
        self.grid_layout.setContentsMargins(padding, padding, padding, padding)
        self.grid_layout.setAlignment(Qt.AlignTop)

        # Initial column calculation based on current widget width
        self._images_per_row = self.get_images_per_row(self.image_size, self.padding)
        self._build_grid()
        self.setLayout(self.grid_layout)
        # Expand horizontally, but keep vertical size to minimum needed (scroll area scrolls instead of stretching rows)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def _build_grid(self):
        # Clear existing items
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.image_paths:
            return

        cols = max(1, self._images_per_row)
        last_row = 0
        for idx, image_path in enumerate(self.image_paths):
            row = idx // cols
            col = idx % cols
            last_row = row
            image_card = ImageCard(image_path, self.image_size, self.padding)
            self.grid_layout.addWidget(image_card, row, col, alignment=Qt.AlignTop)

        # Precisely set our own height to content height to avoid extra blank scroll space.
        rows = last_row + 1
        card_h = self.image_size.height() + 2 * self.padding  # image label + top/bottom padding inside card
        # grid vertical spacing occurs between rows only (rows-1 gaps)
        total_height = (rows * card_h) + max(0, rows - 1) * self.grid_layout.verticalSpacing() + self.grid_layout.contentsMargins().top() + self.grid_layout.contentsMargins().bottom()
        self.setFixedHeight(total_height)


    def _get_images(self,path : str) -> list[str]:
        # Returns a list of image paths from the given directory
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        return [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(supported_formats)]

    def get_images_per_row(self, image_size : QSize, padding_h : int, available_width: int | None = None) -> int:
        '''
        Calculate how many images can fit in a row based on the current window size,
        image size, and horizontal padding.
            :param image_size: QSize object representing the size of each image.
            :param padding_h: Horizontal padding between images.
            :param available_width: Optional explicit width to use (e.g., during external resize hook).
            :return: Number of images that can fit in a single row. 
        '''
        # Always use the CURRENT width of the widget unless an override is supplied
        window_width = self.width() if available_width is None else available_width
        image_width = image_size.width()

        total_h_image_space = image_width + 2 * padding_h

        if not image_width or not window_width or total_h_image_space <= 0:
            return 1
        
        # Each image takes up image_width + 2 * padding_h horizontally
        images_per_row = max(1, window_width // total_h_image_space)
        return images_per_row

    def on_window_resize(self, size : QSize):
        """Backward compatible hook if an external container forwards resize events.

        Directly performs the same recalculation logic as the native resizeEvent without
        trying to fabricate a QResizeEvent (which caused a TypeError previously).
        """
        new_cols = self.get_images_per_row(self.image_size, self.padding, available_width=size.width())
        if new_cols != self._images_per_row:
            self._images_per_row = new_cols
            self._build_grid()

    def resizeEvent(self, event):  # noqa: N802 (Qt naming)
        """Recalculate columns on every resize.

        Qt will prevent the window from shrinking below the layout's minimum size.
        That minimum is driven by one image card (image_size + padding). If you want
        the widget to shrink further, you need to implement dynamic thumbnail scaling
        (scale images smaller than the nominal size when space is tight) or place this
        widget inside a QScrollArea.
        """
        new_cols = self.get_images_per_row(self.image_size, self.padding)
        if new_cols != self._images_per_row:
            self._images_per_row = new_cols
            self._build_grid()
        return super().resizeEvent(event)

    # --- Size hints -----------------------------------------------------
    def minimumSizeHint(self) -> QSize:  # noqa: D401
        """Return the minimum size: one image card including padding."""
        return QSize(self.image_size.width() + 2 * self.padding,
                     self.image_size.height() + 2 * self.padding)

    def sizeHint(self) -> QSize:  # optional, gives a nicer initial size
        cols = max(1, self._images_per_row)
        rows = max(1, (len(self.image_paths) + cols - 1) // cols)
        return QSize(
            cols * (self.image_size.width() + 2 * self.padding),
            rows * (self.image_size.height() + 2 * self.padding)
        )


class ImageGridScrollArea(QScrollArea):
    """Scrollable container for ImageGridWidget.

    Use this in your main window instead of placing ImageGridWidget directly
    if you want vertical scrolling when there are many images.
    """
    def __init__(self, image_size: QSize = QSize(200,200), padding: int = 10, parent=None):
        super().__init__(parent)
        # We'll manage width manually so vertical scroll works predictably
        self.setWidgetResizable(False)
        self._grid = ImageGridWidget(image_size=image_size, padding=padding)
        self.setWidget(self._grid)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._update_inner_width()

    @property
    def grid(self) -> ImageGridWidget:
        return self._grid

    def resizeEvent(self, event):  # noqa: N802
        # Forward width changes to inner grid so it can recalc columns BEFORE layout pass completes
        if self._grid is not None:
            viewport_width = event.size().width()
            # Set inner widget width to viewport width so layout wraps correctly
            self._grid.setFixedWidth(viewport_width)
            self._grid.on_window_resize(QSize(viewport_width, self._grid.height()))
        return super().resizeEvent(event)

    def _update_inner_width(self):
        if self._grid is not None and self.viewport() is not None:
            self._grid.setFixedWidth(self.viewport().width())