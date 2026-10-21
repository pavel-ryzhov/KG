import cv2
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QComboBox, 
                             QSlider, QGroupBox, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from image_processor import ImageProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа 2 - Вариант 9")
        self.setGeometry(100, 100, 1200, 800)

        self.cv_image = None
        self.gray_image = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        control_panel = QVBoxLayout()
        main_layout.addLayout(control_panel, 1)

        self.btn_load = QPushButton("Загрузить изображение")
        self.btn_load.clicked.connect(self.load_image)
        self.btn_load.setMinimumHeight(40)
        control_panel.addWidget(self.btn_load)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Глобальная пороговая обработка", "Сегментация (Границы/Точки)"])
        self.category_combo.currentIndexChanged.connect(self.update_controls)
        control_panel.addWidget(QLabel("Категория обработки:"))
        control_panel.addWidget(self.category_combo)

        self.method_combo = QComboBox()
        self.method_combo.currentIndexChanged.connect(self.process_image)
        control_panel.addWidget(QLabel("Метод:"))
        control_panel.addWidget(self.method_combo)

        self.thresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.thresh_slider.setRange(0, 255)
        self.thresh_slider.setValue(127)
        self.thresh_slider.valueChanged.connect(self.process_image)
        self.slider_label = QLabel("Порог: 127")
        
        self.slider_group = QGroupBox("Настройка ручного порога")
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.slider_label)
        slider_layout.addWidget(self.thresh_slider)
        self.slider_group.setLayout(slider_layout)
        control_panel.addWidget(self.slider_group)

        control_panel.addStretch() 

        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, 4)

        images_layout = QHBoxLayout()
        
        orig_col = QVBoxLayout()
        lbl_orig_title = QLabel("<b>Исходное изображение (Ч/Б)</b>")
        lbl_orig_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_orig_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        orig_col.addWidget(lbl_orig_title)

        self.lbl_original = QLabel("Загрузите картинку")
        self.lbl_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_original.setStyleSheet("background-color: #242424; border: 1px solid #3d3d3d; border-radius: 6px;")
        self.lbl_original.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        orig_col.addWidget(self.lbl_original)
        
        images_layout.addLayout(orig_col, 1)

        res_col = QVBoxLayout()
        lbl_res_title = QLabel("<b>Результат обработки</b>")
        lbl_res_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_res_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        res_col.addWidget(lbl_res_title)

        self.lbl_result = QLabel("Здесь будет результат")
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setStyleSheet("background-color: #242424; border: 1px solid #3d3d3d; border-radius: 6px;")
        self.lbl_result.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        res_col.addWidget(self.lbl_result)

        images_layout.addLayout(res_col, 1)

        right_panel.addLayout(images_layout, 3) 

        hist_layout = QVBoxLayout()
        
        lbl_hist_title = QLabel("<b>Гистограмма исходного изображения</b>")
        lbl_hist_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hist_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        hist_layout.addWidget(lbl_hist_title)

        self.lbl_hist = QLabel()
        self.lbl_hist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hist.setStyleSheet("background-color: #242424; border: 1px solid #3d3d3d; border-radius: 6px;")
        self.lbl_hist.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.lbl_hist.setMinimumHeight(100)
        hist_layout.addWidget(self.lbl_hist)

        right_panel.addLayout(hist_layout, 1) 

        self.update_controls()

    def update_controls(self):
        self.method_combo.blockSignals(True)
        self.method_combo.clear()
        if self.category_combo.currentIndex() == 0:
            self.method_combo.addItems(["Ручной порог (Basic)", "Метод Отсу (Otsu)"])
            self.slider_group.show()
        else:
            self.method_combo.addItems(["Оператор Собеля (Контуры)", "Оператор Лапласа (Точки/Линии)"])
            self.slider_group.hide()
        self.method_combo.blockSignals(False)
        
        if self.cv_image is not None:
            self.process_image()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            img = cv2.imread(file_name)
            if img is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось прочитать изображение.")
                return

            self.cv_image = img
            self.gray_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
            
            self.display_image(self.gray_image, self.lbl_original, is_gray=True)
            
            hist_img = ImageProcessor.get_histogram_image(self.gray_image)
            self.display_image(hist_img, self.lbl_hist, is_gray=False, stretch_to_fill=True)
            
            self.process_image()

    def process_image(self):
        if self.gray_image is None:
            return

        category = self.category_combo.currentIndex()
        method_idx = self.method_combo.currentIndex()
        result_img = None

        if category == 0:
            if method_idx == 0:
                thresh_val = self.thresh_slider.value()
                self.slider_label.setText(f"Порог: {thresh_val}")
                result_img = ImageProcessor.apply_manual_threshold(self.gray_image, thresh_val)
            elif method_idx == 1:
                thresh_val, result_img = ImageProcessor.apply_otsu_threshold(self.gray_image)
                self.slider_label.setText(f"Порог Отсу: {int(thresh_val)}")

        elif category == 1:
            if method_idx == 0:
                result_img = ImageProcessor.apply_sobel(self.gray_image)
            elif method_idx == 1:
                result_img = ImageProcessor.apply_laplacian(self.gray_image)

        if result_img is not None:
            self.display_image(result_img, self.lbl_result, is_gray=True)

    def display_image(self, img, label, is_gray=True, stretch_to_fill=False):
        if is_gray:
            h, w = img.shape
            q_img = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
            
        pixmap = QPixmap.fromImage(q_img)
        
        aspect_ratio_mode = Qt.AspectRatioMode.IgnoreAspectRatio if stretch_to_fill else Qt.AspectRatioMode.KeepAspectRatio
        
        scaled_pixmap = pixmap.scaled(
            label.size(), 
            aspect_ratio_mode, 
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.gray_image is not None:
            self.display_image(self.gray_image, self.lbl_original, is_gray=True)
            self.process_image()
            hist_img = ImageProcessor.get_histogram_image(self.gray_image)
            self.display_image(hist_img, self.lbl_hist, is_gray=False, stretch_to_fill=True)