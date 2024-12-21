# catalog service signals.py
import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Movie, Series, Episode
from django.conf import settings
import json

def get_content_type(instance):
    if isinstance(instance, Movie):
        return 'movie'
    elif isinstance(instance, Series):
        return 'series'
    elif isinstance(instance, Episode):
        return 'episode'
    return None

def send_to_analytics_service(url, data=None, method='post'):
    try:
        if method == 'post':
            response = requests.post(url, json=data)
        elif method == 'put':
            response = requests.put(url, json=data)
        elif method == 'delete':
            response = requests.delete(url)

        if response.status_code not in range(200, 300):
            print(f"Failed to communicate with analytics service: {response.status_code}, {response.content}")
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.content
            print(f"Response data: {response_data}")
    except requests.RequestException as e:
        print(f"Exception occurred: {e}")

@receiver(post_save, sender=Movie)
@receiver(post_save, sender=Series)
@receiver(post_save, sender=Episode)
def sync_with_analytics_service(sender, instance, created, **kwargs):
    base_url = settings.SERVICES['analiticservice'] + '/contents/'


    data = {
        'content_id': instance.id,
        'title': instance.title,
        'duration_minute': getattr(instance, 'duration_minute', None),
        'type': sender.__name__.lower(),
        'thumbnail_image': instance.thumbnail_image.url if hasattr(instance, 'thumbnail_image') and instance.thumbnail_image else None,
        'widescreen_thumbnail_image': instance.widescreen_thumbnail_image.url if hasattr(instance, 'widescreen_thumbnail_image') and instance.widescreen_thumbnail_image else None,
    }


    if isinstance(instance, (Movie, Series)):
        genres = [genre.name for genre in instance.genre.all()]
        release_date = instance.release_date.strftime('%Y-%m-%d') if instance.release_date else None
        data.update({
            'slug': instance.slug,
            'description': instance.description,
            'genre': ', '.join(genres),
            'content_type': get_content_type(instance),
            'release_date': release_date,
            'is_mobile_only': instance.is_mobile_only,
        })

    elif isinstance(instance, Episode):
        series_id = instance.series.id if instance.series else None
        genres = [genre.name for genre in instance.series.genre.all()] if instance.series else []
        release_date = instance.series.release_date.strftime('%Y-%m-%d') if instance.series and instance.series.release_date else None
        thumbnail_image_url = (instance.thumbnail_image.url if hasattr(instance, 'thumbnail_image') and instance.thumbnail_image else
                               instance.series.thumbnail_image.url if instance.series and hasattr(instance.series, 'thumbnail_image') and instance.series.thumbnail_image else
                               None)
        data.update({
            'series_id': series_id,
            'genre': ', '.join(genres),
            'content_type': get_content_type(instance),
            'release_date': release_date,
            'slug': None,
            'description': None,
            'thumbnail_image': thumbnail_image_url
        })

    url = f"{base_url}{instance.id}/" if not created else base_url
    send_to_analytics_service(url, data, 'post' if created else 'put')


    
@receiver(post_delete, sender=Movie)
@receiver(post_delete, sender=Series)
@receiver(post_delete, sender=Episode)
def delete_from_analytics_service(sender, instance, **kwargs):
    base_url = settings.SERVICES['analiticservice'] + '/contents/'
    url = f"{base_url}{instance.id}/"
    send_to_analytics_service(url, method='delete')
