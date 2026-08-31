from apps.face_recognition.services import face_app


def get_embeddings(faces):
    return [face.embedding.tolist() for face in faces]


def get_face_embedding(image):
    faces = face_app.get(image)

    if not faces:
        return None

    if len(faces) > 1:
        raise ValueError("Please provice an image containing only one face.")

    return faces[0].embedding.tolist()