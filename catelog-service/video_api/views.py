from django.http import JsonResponse
from django.views import View
import requests
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from catalog_service.settings import SERVICES

from video_app.models import Content, VideoConversionType
from django.core.exceptions import ObjectDoesNotExist
from video_app.models import Movie, Series, Episode


@method_decorator(csrf_exempt, name='dispatch')
class VideoUploadView(View):

    def validate_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
            return False

        token = auth_header[1]
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(
            SERVICES['authservice'] + '/auth/verify-token', headers=headers)

        return response.status_code == 200

    def post(self, request, *args, **kwargs):
        if not self.validate_token(request):
            return JsonResponse({'status': 'failed', 'message': 'Invalid token or no token provided.'})

        video = request.FILES.get('video')
        content_id = request.POST['content_id']
        is_trailer = request.POST.get('is_trailer', 'false').lower() == 'true'
        video_type = request.POST.get('video_type')
        model_class = get_model_class(video_type)
        print(video_type)
        if model_class is None:
            return JsonResponse({'status': 'failed', 'message': 'Invalid video type.'})

        try:
            content = model_class.objects.get(pk=content_id)
            if hasattr(content, 'conversion_type'):
                video_type = content.conversion_type.video_type
                if is_trailer:
                    video_type = f"{video_type}_TRAILER"
                    print(video_type)
            else:
                # Handle the case for Episode or other models without conversion_type
                video_type = 'EPISODE' if isinstance(
                    content, Episode) else 'UNKNOWN_TYPE'
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Content does not exist.'})
        if video:
            # Define a custom directory path relative to MEDIA_ROOT
            custom_directory_path = os.path.join(
                settings.MEDIA_ROOT, 'custom_videos')

            # Create the directory if it doesn't exist
            if not os.path.exists(custom_directory_path):
                os.makedirs(custom_directory_path)

            # Save the video using FileSystemStorage
            fs = FileSystemStorage(location=custom_directory_path)
            filename = fs.save(video.name, video)

            # Generate the URL to access the video
            full_file_path = os.path.join(fs.location, filename)

            data = {
                'status': 'success',
                'message': 'Video uploaded',
                'video_url': full_file_path,
                'content_id': content_id,
                'video_type': video_type,
            }
            response = requests.post(
                SERVICES['videoconversion'] + "/convert", json=data)
            if response.status_code == 200:
                return JsonResponse({'status': 'success', 'message': 'Video uploaded and conversion initiated', 'video_url': full_file_path})
            else:
                return JsonResponse({'status': 'failed', 'message': f'Video uploaded but conversion failed. Response: {response.text}'})

        return JsonResponse({'status': 'failed', 'message': 'No video uploaded'})


def get_model_class(video_type):
    if video_type == 'MOVIE':
        return Movie
    elif video_type == 'SERIES':
        return Series
    elif video_type == 'EPISODE':
        return Episode
    else:
        return None
