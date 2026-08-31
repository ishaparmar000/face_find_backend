from django.urls import path
from .views import *

urlpatterns = [
    path("upload", PhotoUploadView.as_view(), name="photo-upload"),
    path("scan", FaceScanView.as_view(), name="face-scan"),
    path("home", HomeView.as_view(), name="home"),
    path("gallery", GalleryView.as_view(), name="gallery"),
    path("delete", DeletePhotoView.as_view(), name="delete"),
    path("delete-all", DeleteAllPhotosView.as_view(), name="delete-all"),
]