from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox, QRadioButton
)
from canvas import Canvas
from algorithms import clip_segment_midpoint, clip_polygon_sutherland_hodgman


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №4 — Отсечение (Вариант 9)")
        self.resize(1150, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.canvas = Canvas(self)
        main_layout.addWidget(self.canvas, stretch=4)

        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)

    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        mode_group = QGroupBox("Текущий режим алгоритма")
        mode_layout = QVBoxLayout()
        self.rb_segments = QRadioButton("Часть 1: Отрезки (Средняя точка)")
        self.rb_polygons = QRadioButton("Часть 2: Сазерленд-Ходжман")
        self.rb_segments.setChecked(True)
        mode_layout.addWidget(self.rb_segments)
        mode_layout.addWidget(self.rb_polygons)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        file_group = QGroupBox("Загрузка данных")
        file_layout = QVBoxLayout()
        btn_load = QPushButton("Загрузить файл")
        btn_load.clicked.connect(self.load_file)
        
        btn_demo = QPushButton("Загрузить демо")
        btn_demo.clicked.connect(self.load_demo)
        
        file_layout.addWidget(btn_load)
        file_layout.addWidget(btn_demo)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        act_group = QGroupBox("Управление")
        act_layout = QVBoxLayout()
        btn_run = QPushButton("Выполнить отсечение")
        btn_run.setStyleSheet("font-weight: bold; background-color: #2b78e4; color: white; padding: 7px; border-radius: 4px;")
        btn_run.clicked.connect(self.run_clipping)

        btn_reset_view = QPushButton("Сбросить зум и камеру")
        btn_reset_view.clicked.connect(self.canvas.reset_view)

        act_layout.addWidget(btn_run)
        act_layout.addWidget(btn_reset_view)
        act_group.setLayout(act_layout)
        layout.addWidget(act_group)

        status_group = QGroupBox("Информация о данных")
        status_layout = QVBoxLayout()
        self.lbl_status = QLabel("Загрузите файл или выберите демо.")
        self.lbl_status.setWordWrap(True)
        status_layout.addWidget(self.lbl_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        legend_group = QGroupBox("Легенда")
        leg_layout = QVBoxLayout()
        leg_layout.addWidget(QLabel("🟧 Окно отсечения"))
        leg_layout.addWidget(QLabel("🟥 Исходные отрезки"))
        leg_layout.addWidget(QLabel("🟦 Исходный многоугольник"))
        leg_layout.addWidget(QLabel("🟩 Отсечённая часть (результат)"))
        legend_group.setLayout(leg_layout)
        layout.addWidget(legend_group)

        layout.addStretch()
        return panel

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;All Files (*)")
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            if len(lines) < 2:
                raise ValueError("Файл содержит недостаточно данных!")

            rect_coords = list(map(float, lines[-1].split()))
            if len(rect_coords) != 4:
                raise ValueError("Последняя строка должна задавать окно (xmin ymin xmax ymax)!")

            clip_rect = tuple(rect_coords)

            first_data_line = list(map(float, lines[1].split()))
            
            self.canvas.segments = []
            self.canvas.polygons = []
            self.canvas.clipped_segments = []
            self.canvas.clipped_polygons = []
            self.canvas.clip_rect = clip_rect

            if len(first_data_line) == 4:
                n = int(lines[0])
                segments = []
                for i in range(1, n + 1):
                    coords = list(map(float, lines[i].split()))
                    segments.append(((coords[0], coords[1]), (coords[2], coords[3])))

                self.canvas.segments = segments
                self.rb_segments.setChecked(True)
                self.lbl_status.setText(f"Файл определён как: **Отрезки**\nЗагружено отрезков: {len(segments)}")

            elif len(first_data_line) == 2:
                n = int(lines[0])
                polygon = []
                for i in range(1, n + 1):
                    coords = list(map(float, lines[i].split()))
                    polygon.append((coords[0], coords[1]))

                self.canvas.polygons = [polygon]
                self.rb_polygons.setChecked(True)
                self.lbl_status.setText(f"Файл определён как: **Многоугольник**\nВершин: {len(polygon)}")
            else:
                raise ValueError(f"Неизвестный формат строки: ожидалось 2 или 4 координаты, получено {len(first_data_line)}.")

            self.canvas.reset_view()
            self.canvas.update()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось прочитать файл:\n{str(e)}")

    def load_demo(self):
        if self.rb_segments.isChecked():
            self.canvas.clip_rect = (-10, -8, 10, 8)
            self.canvas.segments = [
                ((-15, -12), (15, 12)),
                ((-12, 5), (12, 5)),
                ((-5, 12), (5, -12)),
                ((-15, -5), (-12, 5)),
                ((0, 0), (6, 6)),
                ((12, -2), (14, 10))
            ]
            self.canvas.polygons = []
            self.canvas.clipped_segments = []
            self.canvas.clipped_polygons = []
            self.lbl_status.setText("Загружено демо: 6 отрезков.\nАлгоритм: Деление пополам.")
        else:
            self.canvas.clip_rect = (-8, -8, 8, 8)
            self.canvas.polygons = [
                [(-12, 0), (-6, 11), (6, 11), (12, 2), (9, -10), (0, -12), (-10, -6)]
            ]
            self.canvas.segments = []
            self.canvas.clipped_segments = []
            self.canvas.clipped_polygons = []
            self.lbl_status.setText("Загружено демо: Многоугольник (7 вершин).\nАлгоритм: Сазерленд-Ходжман.")

        self.canvas.reset_view()

    def run_clipping(self):
        if not self.canvas.clip_rect:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите входные данные!")
            return

        if self.rb_segments.isChecked():
            clipped = []
            for seg in self.canvas.segments:
                res = clip_segment_midpoint(seg[0], seg[1], self.canvas.clip_rect)
                if res is not None:
                    clipped.append(res)
            self.canvas.clipped_segments = clipped
            self.lbl_status.setText(f"Отсечение отрезков выполнено.\nВидимых частей: {len(clipped)}")
        else:
            clipped = []
            for poly in self.canvas.polygons:
                res = clip_polygon_sutherland_hodgman(poly, self.canvas.clip_rect)
                if res:
                    clipped.append(res)
            self.canvas.clipped_polygons = clipped
            verts_count = len(clipped[0]) if clipped else 0
            self.lbl_status.setText(f"Отсечение многоугольника выполнено.\nВершин в итоге: {verts_count}")

        self.canvas.update()