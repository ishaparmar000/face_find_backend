import cv2

from .services import face_app

def detect_faces(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    return face_app.get(image)