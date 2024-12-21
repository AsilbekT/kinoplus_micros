from django.urls import path, include
from .views import VideoUploadView


urlpatterns = [
    path('upload-video/', VideoUploadView.as_view(), name='upload-video'),
]
