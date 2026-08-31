from django.db import models
from pgvector.django import VectorField


class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id}"

class FaceEmbedding(models.Model):
    photo = models.ForeignKey(
        Photo, on_delete=models.CASCADE, related_name='face_embeddings'
    )
    embedding = VectorField(dimensions=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FaceEmbedding {self.id} - Photo {self.photo.id}"