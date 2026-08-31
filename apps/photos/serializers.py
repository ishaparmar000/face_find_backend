from rest_framework import serializers
from .models import Photo



class GalleryPhotoSerializer(serializers.ModelSerializer):

    faces_count = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "image_url", "faces_count", "created_at"]

    def get_image_url(self, obj):
        return obj.image.url
        

class MultiplePhotoUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
    )


class FaceScanSerializer(serializers.Serializer):
    face = serializers.ImageField()

class DeletePhotoSerializer(serializers.Serializer):
    photo_id = serializers.IntegerField()