import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSpinBox, QComboBox, QPushButton, QSlider, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
import algorithms
from canvas import GridCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Базовые растровые алгоритмы (ЛР 3)")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_layout = QVBoxLayout(control_panel)

        self.algo_combo = QComboBox()
        self.algo_combo.addItems([
            "Пошаговый алгоритм",
            "Алгоритм ЦДА",
            "Брезенхем (отрезок)",
            "Брезенхем (окружность)",
            "Алгоритм Кастла-Питвея",
            "Алгоритм Ву (Сглаживание)"
        ])
        self.algo_combo.currentIndexChanged.connect(self.toggle_inputs)
        control_layout.addWidget(QLabel("<b>Выберите алгоритм:</b>"))
        control_layout.addWidget(self.algo_combo)

        self.line_group = QGroupBox("Координаты отрезка")
        line_layout = QFormLayout(self.line_group)
        self.spin_x1 = self.create_spinbox(-100, 100, 1)
        self.spin_y1 = self.create_spinbox(-100, 100, 1)
        self.spin_x2 = self.create_spinbox(-100, 100, 8)
        self.spin_y2 = self.create_spinbox(-100, 100, 5)
        line_layout.addRow("X1:", self.spin_x1)
        line_layout.addRow("Y1:", self.spin_y1)
        line_layout.addRow("X2:", self.spin_x2)
        line_layout.addRow("Y2:", self.spin_y2)
        control_layout.addWidget(self.line_group)

        self.circle_group = QGroupBox("Координаты окружности")
        circle_layout = QFormLayout(self.circle_group)
        self.spin_xc = self.create_spinbox(-100, 100, 0)
        self.spin_yc = self.create_spinbox(-100, 100, 0)
        self.spin_r = self.create_spinbox(1, 100, 7)
        circle_layout.addRow("Центр X:", self.spin_xc)
        circle_layout.addRow("Центр Y:", self.spin_yc)
        circle_layout.addRow("Радиус R:", self.spin_r)
        control_layout.addWidget(self.circle_group)
        self.circle_group.setVisible(False)

        control_layout.addWidget(QLabel("<b>Масштаб сетки:</b>"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(5)
        self.zoom_slider.setMaximum(50)
        self.zoom_slider.setValue(20)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        control_layout.addWidget(self.zoom_slider)

        self.btn_draw = QPushButton("Нарисовать")
        self.btn_draw.setMinimumHeight(40)
        self.btn_draw.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_draw.clicked.connect(self.on_draw)
        control_layout.addWidget(self.btn_draw)

        self.time_label = QLabel("Время выполнения (10 000 итераций):\n-")
        control_layout.addWidget(self.time_label)

        control_layout.addStretch()

        self.canvas = GridCanvas()

        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.on_draw()
        else:
            super().keyPressEvent(event)
    

    def create_spinbox(self, min_val, max_val, default_val):
        """Вспомогательная функция для создания полей ввода"""
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default_val)
        return spin

    def toggle_inputs(self):
        """Переключает видимость полей ввода в зависимости от алгоритма (Дружелюбный интерфейс)"""
        algo_name = self.algo_combo.currentText()
        if "окружность" in algo_name.lower():
            self.line_group.setVisible(False)
            self.circle_group.setVisible(True)
        else:
            self.line_group.setVisible(True)
            self.circle_group.setVisible(False)

    def on_zoom_changed(self, value):
        self.canvas.set_zoom(value)

    def on_draw(self):
        """Главная функция запуска вычислений, замеров и отрисовки"""
        algo_idx = self.algo_combo.currentIndex()
        
        x1, y1 = self.spin_x1.value(), self.spin_y1.value()
        x2, y2 = self.spin_x2.value(), self.spin_y2.value()
        xc, yc = self.spin_xc.value(), self.spin_yc.value()
        r = self.spin_r.value()

        is_wu = (algo_idx == 5)

        if algo_idx == 0:
            target_func = lambda: algorithms.step_algorithm(x1, y1, x2, y2)
        elif algo_idx == 1:
            target_func = lambda: algorithms.dda_algorithm(x1, y1, x2, y2)
        elif algo_idx == 2:
            target_func = lambda: algorithms.bresenham_line(x1, y1, x2, y2)
        elif algo_idx == 3:
            target_func = lambda: algorithms.bresenham_circle(xc, yc, r)
        elif algo_idx == 4:
            target_func = lambda: algorithms.castle_pitteway(x1, y1, x2, y2)
        elif algo_idx == 5:
            target_func = lambda: algorithms.wu_line(x1, y1, x2, y2)
        else:
            return

        pixels = target_func()
        self.canvas.set_pixels(pixels, is_wu=is_wu)

        iterations = 10000
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            target_func()
                
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        self.time_label.setText(f"Время выполнения (10 000 итераций):\n{elapsed_ms:.4f} мс")