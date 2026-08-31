import cv2
from apps.face_recognition.services import face_app

IMAGE_PATH = "test_images/test.png"

image = cv2.imread(IMAGE_PATH)

if image is None: 
    raise FileNotFoundError(f"Image not found at {IMAGE_PATH}")

faces = face_app.get(image)

print(f"Face detected: {len(faces)}")

for index, face in enumerate(faces, start=1):
    print(f"\nFace {index}")
    print("Bounding box:", face.bbox)
    print("Embedding shape:", face.embedding.shape)
    print("Embedding length:", len(face.embedding))
