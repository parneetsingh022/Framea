from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QGridLayout, QScrollArea, QSizePolicy
)

from PySide6.QtGui import QPixmap, QCursor

from PySide6.QtCore import Qt, QSize
import os



class ImageCard(QWidget):
    def __init__(self, image_path: str, image_size: QSize, padding: int):
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

        self._layout = layout  # keep reference for fast padding updates
        self._image_path = image_path
        self._image_size = image_size

    def set_internal_padding(self, padding: int):
        """Update internal margins without recreating the widget."""
        self._layout.setContentsMargins(padding, padding, padding, padding)

    def _get_scalled_pixmap(self, pixmap : QPixmap, size : QSize) -> QPixmap:
        # Scale and crop the pixmap to be square
        scaled_pixmap = pixmap.scaled(size.width(), size.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        rect = scaled_pixmap.rect()
        x = (rect.width() - size.width()) // 2
        y = (rect.height() - size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x, y, size.width(), size.height())
        return cropped_pixmap

class ImageGridWidget(QWidget):
    def __init__(self, image_size: QSize, padding: float):
        super().__init__()
        self.image_size = image_size
        self._images_per_row = 1
        self._padding_input = padding  # store original user value
        self.gap = 0
        self.card_inner_padding = 0
        self._cards: list[ImageCard] = []  # cache of ImageCard widgets for reuse

        # TODO: make image directory configurable / injectable
        self.image_paths = self._get_images("C:\\Users\\parne\\Pictures\\Screenshots")

        # --- Layout construction order matters so we can apply flush margins everywhere ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        main_layout = QHBoxLayout()
        main_layout.addLayout(self.grid_layout)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Apply initial padding AFTER parent layout exists so flush mode can zero its margins too
        self._apply_padding(self._padding_input)

        # Initial column calculation based on current widget width (gap computed above)
        self._images_per_row = self.get_images_per_row(self.image_size, self.gap)
        self._build_grid(reuse=True)

    # --- Padding / gap logic ------------------------------------------
    def _apply_padding(self, padding: float):
        """Interpret user padding value and update layout metrics.

        Rules:
          padding == 0 -> flush mode (images touch): gap=0, margins=0, inner=0
          0 < padding < 1 -> fraction of image width (at least 1px)
          padding >= 1 -> absolute pixels
        """
        self._padding_input = padding
        if padding == 0:
            gap = 0
        elif 0 < padding < 1:
            gap = max(1, int(self.image_size.width() * padding))
        else:
            gap = int(padding)

        self.gap = gap
        # Inner padding only when we have a visibly larger gap (avoid double spacing)
        self.card_inner_padding = 0 if gap <= 4 else max(1, gap // 4)
        parent_layout = self.layout()

        if gap == 0:
            # STRICT FLUSH MODE: remove every spacing/margin source
            self.grid_layout.setHorizontalSpacing(0)
            self.grid_layout.setVerticalSpacing(0)
            self.grid_layout.setContentsMargins(0, 0, 0, 0)
            if parent_layout is not None:
                parent_layout.setSpacing(0)
                parent_layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.grid_layout.setHorizontalSpacing(gap)
            self.grid_layout.setVerticalSpacing(gap)
            self.grid_layout.setContentsMargins(gap, gap, gap, gap)
            if parent_layout is not None:
                # Mirror outer margins so centering remains visually balanced
                parent_layout.setSpacing(gap)
                parent_layout.setContentsMargins(gap, gap, gap, gap)

    def set_padding(self, padding: float):
        """Public method to change padding at runtime."""
        self._apply_padding(padding)
        # Recompute columns because effective width per image changed
        self._images_per_row = self.get_images_per_row(self.image_size, self.gap)
        self._build_grid(reuse=True)

    def _build_grid(self, reuse: bool = False):
        """(Re)build the grid layout.

        If reuse=True, we DO NOT destroy and recreate ImageCard widgets; instead we:
          * Ensure we have enough cached cards (create only missing ones)
          * Update internal padding on existing cards
          * Reposition them in the layout

        This drastically lowers churn during window resizes where only geometry changes.
        """
        # Remove all layout items but don't delete widgets if reuse requested
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            # Don't delete the widget if reuse; just detach it
            if not reuse:
                w = item.widget()
                if w:
                    w.deleteLater()

        if not self.image_paths:
            return

        # Ensure card cache large enough
        if reuse:
            if len(self._cards) < len(self.image_paths):
                for i in range(len(self._cards), len(self.image_paths)):
                    self._cards.append(ImageCard(self.image_paths[i], self.image_size, padding=self.card_inner_padding))
            # Update internal padding on all cached cards (cheap)
            for card in self._cards:
                card.set_internal_padding(self.card_inner_padding)
        else:
            # Fresh construction path
            self._cards = [ImageCard(p, self.image_size, padding=self.card_inner_padding) for p in self.image_paths]

        cols = max(1, self._images_per_row)
        last_row = 0
        for idx, card in enumerate(self._cards):
            if idx >= len(self.image_paths):
                break
            row = idx // cols
            col = idx % cols
            last_row = row
            self.grid_layout.addWidget(card, row, col, alignment=Qt.AlignTop)

        # Hide any extra cached cards (if image list shrank) without deleting; future reuse possible
        for extra in self._cards[len(self.image_paths):]:
            extra.setParent(None)
            extra.hide()

        # Precisely set our own height to content height to avoid extra blank scroll space.
        rows = last_row + 1
        card_h = self.image_size.height() + 2 * self.card_inner_padding
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
        # Each image cell occupies its width plus exactly ONE gap to its right except last column.
        # For fitting calculation we treat each image as (image_width + gap). When gap=0 (flush) this collapses.
        total_h_image_space = image_width + padding_h
        if not image_width or not window_width or total_h_image_space <= 0:
            return 1
        images_per_row = max(1, window_width // total_h_image_space)
        return images_per_row

    # Convenience helper (not strictly required but useful for debugging / clarity)
    def is_flush(self) -> bool:
        return self.gap == 0

    def on_window_resize(self, size : QSize):
        """Backward compatible hook if an external container forwards resize events.

        Directly performs the same recalculation logic as the native resizeEvent without
        trying to fabricate a QResizeEvent (which caused a TypeError previously).
        """
        new_cols = self.get_images_per_row(self.image_size, self.gap, available_width=size.width())
        if new_cols != self._images_per_row:
            self._images_per_row = new_cols
            self._build_grid(reuse=True)

    def resizeEvent(self, event):  # noqa: N802 (Qt naming)
        """Recalculate columns on every resize.

        Qt will prevent the window from shrinking below the layout's minimum size.
        That minimum is driven by one image card (image_size + padding). If you want
        the widget to shrink further, you need to implement dynamic thumbnail scaling
        (scale images smaller than the nominal size when space is tight) or place this
        widget inside a QScrollArea.
        """
        new_cols = self.get_images_per_row(self.image_size, self.gap)
        if new_cols != self._images_per_row:
            self._images_per_row = new_cols
            self._build_grid(reuse=True)
        return super().resizeEvent(event)

    # --- Size hints -----------------------------------------------------
    def minimumSizeHint(self) -> QSize:  # noqa: D401
        """Return the minimum size: one image card including padding."""
        return QSize(self.image_size.width() + 2 * self.card_inner_padding,
        self.image_size.height() + 2 * self.card_inner_padding)

    def sizeHint(self) -> QSize:  # optional, gives a nicer initial size
        cols = max(1, self._images_per_row)
        rows = max(1, (len(self.image_paths) + cols - 1) // cols)
        return QSize(
            cols * (self.image_size.width() + self.gap),
            rows * (self.image_size.height() + self.gap)
        )


class ImageGridScrollArea(QScrollArea):
    """Scrollable container for ImageGridWidget.

    Use this in your main window instead of placing ImageGridWidget directly
    if you want vertical scrolling when there are many images.
    """
    def __init__(self, image_size: QSize = QSize(200,200), padding: int = 0.01, parent=None):
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