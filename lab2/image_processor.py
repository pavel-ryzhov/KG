import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def apply_manual_threshold(image, threshold_value):
        _, result = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        return result

    @staticmethod
    def apply_otsu_threshold(image):
        thresh_val, result = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh_val, result

    @staticmethod
    def apply_sobel(image):
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(sobelx, sobely)
        return cv2.convertScaleAbs(magnitude)

    @staticmethod
    def apply_laplacian(image):
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return cv2.convertScaleAbs(laplacian)

    @staticmethod
    def get_histogram_image(image):
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        
        hist_w, hist_h = 800, 150
        pad = 10 
        
        hist_image = np.zeros((hist_h + pad*2, hist_w + pad*2, 3), dtype=np.uint8)
        hist_image[:] = (45, 45, 45)
        
        for y in range(0, hist_h, 50):
            cv2.line(hist_image, (pad, y + pad), (hist_w + pad, y + pad), (70, 70, 70), 1)
            
        cv2.normalize(hist, hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
        hist = np.round(hist).flatten().astype(int)
        
        pts = [(pad, hist_h + pad)]
        for i in range(256):
            x = pad + int(hist_w / 256 * i)
            y = pad + hist_h - hist[i]
            pts.append((x, y))
        pts.append((pad + hist_w, hist_h + pad))
        
        pts = np.array([pts], dtype=np.int32)
        
        cv2.fillPoly(hist_image, pts, (210, 120, 60))
        cv2.polylines(hist_image, pts, False, (255, 170, 80), 2)
            
        return hist_image