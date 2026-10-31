from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRect

class GridCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell_size = 20
        self.pixels = []
        self.wu_pixels = []
        
    def set_pixels(self, pixels, is_wu=False):
        """Передает список пикселей для отрисовки"""
        if is_wu:
            self.wu_pixels = pixels
            self.pixels = []
        else:
            self.pixels = pixels
            self.wu_pixels = []
        self.update()
        
    def set_zoom(self, value):
        """Изменение масштаба"""
        self.cell_size = value
        self.update()

    def paintEvent(self, event):
        """Событие отрисовки (вызывается системой)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        width = self.width()
        height = self.height()
        
        cx = width // 2
        cy = height // 2

        painter.fillRect(0, 0, width, height, QColor(255, 255, 255))

        painter.setPen(QPen(QColor(220, 220, 220), 1))
        
        for x in range(cx % self.cell_size, width, self.cell_size):
            painter.drawLine(x, 0, x, height)
        for y in range(cy % self.cell_size, height, self.cell_size):
            painter.drawLine(0, y, width, y)

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(0, cy, width, cy)
        painter.drawLine(cx, 0, cx, height)

        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        
        for i in range(-cx // self.cell_size, width // self.cell_size):
            if i != 0:
                screen_x = cx + i * self.cell_size
                painter.drawLine(screen_x, cy - 3, screen_x, cy + 3)
                painter.drawText(screen_x - 10, cy + 15, str(i))
                
        for i in range(-cy // self.cell_size, height // self.cell_size):
            if i != 0:
                screen_y = cy - i * self.cell_size
                painter.drawLine(cx - 3, screen_y, cx + 3, screen_y)
                painter.drawText(cx + 8, screen_y + 4, str(i))

        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        for x, y in self.pixels:
            screen_x = cx + x * self.cell_size
            screen_y = cy - y * self.cell_size - self.cell_size
            painter.drawRect(screen_x, screen_y, self.cell_size, self.cell_size)
            
        for x, y, alpha in self.wu_pixels:
            screen_x = cx + x * self.cell_size
            screen_y = cy - y * self.cell_size - self.cell_size
            color = QColor(0, 0, 255)
            color.setAlphaF(alpha)
            painter.setBrush(color)
            painter.drawRect(screen_x, screen_y, self.cell_size, self.cell_size)