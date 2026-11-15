import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QPolygonF
from PyQt6.QtCore import Qt, QPointF


class Canvas(QWidget):
    MIN_SCALE = 2.0
    MAX_SCALE = 250.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.clip_rect = None
        self.segments = []
        self.clipped_segments = []
        self.polygons = []
        self.clipped_polygons = []

        self.scale = 20.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.last_mouse_pos = None

    def reset_view(self):
        self.scale = 20.0
        self.offset_x = self.width() / 2.0
        self.offset_y = self.height() / 2.0
        self.update()

    def resizeEvent(self, event):
        if self.offset_x == 0 and self.offset_y == 0:
            self.reset_view()
        super().resizeEvent(event)

    def to_screen(self, x, y):
        """Преобразование мировых координат в экранные."""
        sx = self.offset_x + x * self.scale
        sy = self.offset_y - y * self.scale
        return QPointF(sx, sy)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e24"))

        self.draw_grid(painter)
        self.draw_clip_window(painter)
        self.draw_polygons(painter)
        self.draw_segments(painter)

    def draw_grid(self, painter: QPainter):
        w, h = self.width(), self.height()

        # Вычисляем адаптивный шаг сетки, чтобы линий всегда было адекватное количество
        target_pixel_step = 60.0
        raw_step = target_pixel_step / self.scale
        power = math.floor(math.log10(max(raw_step, 1e-6)))
        fraction = raw_step / (10 ** power)

        if fraction < 2:
            step = 1 * (10 ** power)
        elif fraction < 5:
            step = 2 * (10 ** power)
        else:
            step = 5 * (10 ** power)

        if step <= 0:
            step = 1

        start_x = int(math.floor((-self.offset_x) / (self.scale * step))) * step
        end_x = int(math.ceil((w - self.offset_x) / (self.scale * step))) * step

        start_y = int(math.floor((self.offset_y - h) / (self.scale * step))) * step
        end_y = int(math.ceil((self.offset_y) / (self.scale * step))) * step

        painter.setPen(QPen(QColor("#2d2d38"), 1, Qt.PenStyle.SolidLine))
        painter.setFont(QFont("Consolas", 8))

        for gx in self._frange(start_x, end_x + step, step):
            p1 = self.to_screen(gx, -10000)
            p2 = self.to_screen(gx, 10000)
            painter.drawLine(p1, p2)
            if abs(gx) > 1e-5:
                pos = self.to_screen(gx, 0)
                painter.setPen(QColor("#666677"))
                painter.drawText(int(pos.x() + 2), int(self.offset_y - 4), f"{gx:g}")
                painter.setPen(QPen(QColor("#2d2d38"), 1))

        for gy in self._frange(start_y, end_y + step, step):
            p1 = self.to_screen(-10000, gy)
            p2 = self.to_screen(10000, gy)
            painter.drawLine(p1, p2)
            if abs(gy) > 1e-5:
                pos = self.to_screen(0, gy)
                painter.setPen(QColor("#666677"))
                painter.drawText(int(self.offset_x + 4), int(pos.y() - 2), f"{gy:g}")
                painter.setPen(QPen(QColor("#2d2d38"), 1))

        painter.setPen(QPen(QColor("#888899"), 2))
        painter.drawLine(QPointF(0, self.offset_y), QPointF(w, self.offset_y))
        painter.drawLine(QPointF(self.offset_x, 0), QPointF(self.offset_x, h))

        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(int(w - 25), int(self.offset_y - 8), "X")
        painter.drawText(int(self.offset_x + 8), 20, "Y")

    def _frange(self, start, stop, step):
        count = 0
        current = start
        while current <= stop and count < 1000:
            yield current
            current += step
            count += 1

    def draw_clip_window(self, painter: QPainter):
        if not self.clip_rect:
            return
        xmin, ymin, xmax, ymax = self.clip_rect
        p_top_left = self.to_screen(xmin, ymax)
        p_bottom_right = self.to_screen(xmax, ymin)

        w = p_bottom_right.x() - p_top_left.x()
        h = p_bottom_right.y() - p_top_left.y()

        painter.setBrush(QBrush(QColor(255, 165, 0, 30)))
        painter.setPen(QPen(QColor(255, 165, 0, 230), 2, Qt.PenStyle.DashLine))
        painter.drawRect(int(p_top_left.x()), int(p_top_left.y()), int(w), int(h))

    def draw_segments(self, painter: QPainter):
        painter.setPen(QPen(QColor("#ff5555"), 1.5, Qt.PenStyle.DashDotLine))
        for p1, p2 in self.segments:
            s1 = self.to_screen(*p1)
            s2 = self.to_screen(*p2)
            painter.drawLine(s1, s2)

        painter.setPen(QPen(QColor("#00ff66"), 3))
        for p1, p2 in self.clipped_segments:
            s1 = self.to_screen(*p1)
            s2 = self.to_screen(*p2)
            painter.drawLine(s1, s2)
            painter.drawEllipse(s1, 3.5, 3.5)
            painter.drawEllipse(s2, 3.5, 3.5)

    def draw_polygons(self, painter: QPainter):
        painter.setPen(QPen(QColor("#4da6ff"), 1.5, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for poly in self.polygons:
            poly_f = QPolygonF([self.to_screen(*pt) for pt in poly])
            painter.drawPolygon(poly_f)

        painter.setPen(QPen(QColor("#00ffcc"), 2.5))
        painter.setBrush(QBrush(QColor(0, 255, 204, 70)))
        for poly in self.clipped_polygons:
            poly_f = QPolygonF([self.to_screen(*pt) for pt in poly])
            painter.drawPolygon(poly_f)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        new_scale = self.scale * factor

        if self.MIN_SCALE <= new_scale <= self.MAX_SCALE:
            self.scale = new_scale
            self.update()

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos and (event.buttons() & (Qt.MouseButton.RightButton | Qt.MouseButton.MiddleButton | Qt.MouseButton.LeftButton)):
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None