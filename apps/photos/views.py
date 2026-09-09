from pathlib import Path

import cv2
from django.db.models import Count
import numpy as np
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.face_recognition.detector import detect_faces
from apps.face_recognition.embeddings import get_embeddings, get_face_embedding
from apps.photos.api import validation_error_response

from .models import FaceEmbedding, Photo
from .serializers import *


class HomeView(APIView):
    def get(self, request):

        photos_count = Photo.objects.count()
        faces_count = FaceEmbedding.objects.count()

        return Response({
            "status": True,
            "message": "Home data fetched successfully.",
            "data": {
                "stats": {
                    "photos": photos_count,
                    "faces": faces_count,
                    "searches": 0,
                },
            },
        }, status=status.HTTP_200_OK)


class GalleryView(APIView):

    def get(self, request):
        photos = (
            Photo.objects
            .annotate(faces_count=Count("face_embeddings"))
            .order_by("-created_at")
        )

        serializer = GalleryPhotoSerializer(
            photos,
            many=True,
            context={"request": request},
        )

        return Response({
            "status": True,
            "message": "Gallery fetched successfully.",
            "data": {
                "count": photos.count(),
                "photos": serializer.data,
            },
        }, status=status.HTTP_200_OK)

class PhotoUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        serializer = MultiplePhotoUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error_response(serializer)

        images = serializer.validated_data["images"]

        uploaded_photos = []

        for image in images:

            photo = Photo.objects.create(image=image)

            image_path = Path(settings.MEDIA_ROOT) / photo.image.name

            try:
                faces = detect_faces(str(image_path))
                embeddings = get_embeddings(faces)

                FaceEmbedding.objects.bulk_create([
                    FaceEmbedding(
                        photo=photo,
                        embedding=embedding,
                    )
                    for embedding in embeddings
                ])

                uploaded_photos.append({
                    "id": photo.id,
                    "image_url": photo.image.url,
                    "faces_detected": len(faces),
                })

            except Exception as exc:
                photo.delete()
                return Response({
                    "status": False,
                    "message": "Failed to process one of the uploaded images.",
                    "error": str(exc),
                }, status=status.HTTP_200_OK)

        return Response({
            "status": True,
            "message": "Photos uploaded successfully.",
            "data": {
                "count": len(uploaded_photos),
                "photos": uploaded_photos,
            },
        }, status=status.HTTP_200_OK)

class FaceScanView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        serializer = FaceScanSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error_response(serializer)

        scan_file = serializer.validated_data["face"]

        scan_image = cv2.imdecode(
            np.frombuffer(
                scan_file.read(),
                dtype=np.uint8,
            ),
            cv2.IMREAD_COLOR,
        )

        if scan_image is None:
            return Response({
                "status": False,
                "message": "Could not read the uploaded image.",
            }, status=status.HTTP_200_OK)

        try:
            embedding = get_face_embedding(scan_image)

            if embedding is None:
                return Response({
                    "status": False,
                    "message": "No face detected in the image.",
                }, status=status.HTTP_200_OK)

        except ValueError as exc:

            return Response({
                "status": False,
                "message": str(exc),
            }, status=status.HTTP_200_OK)

        except Exception as exc:

            return Response({
                "status": False,
                "message": "Failed to process the face image.",
                "error": str(exc),
            }, status=status.HTTP_200_OK)

        matches = []
        embeddings_qs = list(FaceEmbedding.objects.select_related("photo"))

        for face_embedding in embeddings_qs:
            stored = np.asarray(face_embedding.embedding, dtype=np.float32)
            query = np.asarray(embedding, dtype=np.float32)

            if stored.shape != query.shape:
                continue

            denom = np.linalg.norm(stored) * np.linalg.norm(query)
            cosine_similarity = float(np.dot(stored, query) / denom) if denom else 0.0
            distance = 1.0 - cosine_similarity

            if distance <= 0.40:
                matches.append((distance, face_embedding))

        matches.sort(key=lambda item: item[0])

        photos = []
        seen_photo_ids = set()

        for distance, face_embedding in matches:

            photo = face_embedding.photo

            if photo.id in seen_photo_ids:
                continue

            seen_photo_ids.add(photo.id)

            photos.append({
                "id": photo.id,
                "image_url": request.build_absolute_uri(photo.image.url),
                "faces_count": photo.face_embeddings.count(),
                "created_at": photo.created_at,
            })

        return Response({
            "status": True,
            "message": "Matching photos fetched successfully.",
            "data": {
                "count": len(photos),
                "photos": photos,
            },
        }, status=status.HTTP_200_OK)



class DeletePhotoView(APIView):

    def post(self, request):

        serializer = DeletePhotoSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error_response(serializer)

        photo_id = serializer.validated_data["photo_id"]

        photo = Photo.objects.filter(id=photo_id).first()

        if photo is None:
            return Response({
                "status": False,
                "message": "Photo not found."
            }, status=status.HTTP_200_OK)

        photo.delete()

        return Response({
            "status": True,
            "message": "Photo deleted successfully."
        }, status=status.HTTP_200_OK)


class DeleteAllPhotosView(APIView):

    def post(self, request):

        Photo.objects.all().delete()

        return Response({
            "status": True,
            "message": "All photos deleted successfully."
        }, status=status.HTTP_200_OK)