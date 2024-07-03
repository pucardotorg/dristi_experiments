import numpy as np
import cv2

def normalize_image(image):
    image = image.astype(np.float64)
    return image / 255.0

def compute_edge_features(image):
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    sobel_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)

    roberts_x = cv2.filter2D(image, -1, np.array([[1, 0], [0, -1]]))
    roberts_y = cv2.filter2D(image, -1, np.array([[0, 1], [-1, 0]]))
    roberts_magnitude = np.sqrt(roberts_x ** 2 + roberts_y ** 2)

    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    def calculate_features(edge_map):
        return {
            'mean': np.mean(edge_map),
            'variance': np.var(edge_map),
            'max': np.max(edge_map),
        }

    features = []
    for edge_map in [sobel_magnitude, roberts_magnitude, laplacian]:
        feats = calculate_features(edge_map)
        features.extend([feats['mean'], feats['variance'], feats['max']])

    return np.array(features)