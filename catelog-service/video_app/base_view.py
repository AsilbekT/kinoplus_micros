import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from catalog_service.settings import SERVICES
from django.db.models import Q
from django.utils import timezone
from video_app.serializers import CommentSerializer, FavoriteContentSerializer
from .utils import standardResponse
from .models import Episode, FavoriteContent, UserSubscription, Movie, Series, Comment, ContentType
from django.shortcuts import get_object_or_404


import logging

logger = logging.getLogger(__name__)

class DeviceCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.is_request_from_mac(request):
            logger.info(f"Request from Mac: {request.META.get('REMOTE_ADDR')}")
        return super().dispatch(request, *args, **kwargs)

    def is_request_from_mac(self, request):
        user_agent = request.headers.get('User-Agent', '').lower()
        return 'macintosh' in user_agent or 'mac os x' in user_agent


class BaseViewSet(viewsets.ModelViewSet):
    def validate_token(self, request):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
            if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
                return False, None, None

            token = auth_header[1]
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                SERVICES['authservice'] + '/auth/verify-token', headers=headers)
            if response.status_code == 200:
                return True, response.json()['data'], token
            else:
                return False, None, None
        except Exception as e:
            # Log the exception if necessary
            return False, None, None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return standardResponse(status="success", message="Items retrieved", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return standardResponse(status="success", message="Item created", data=serializer.data)
        return standardResponse(status="error", message="Invalid data", data=serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.pop('slug', None)
        if slug:
            instance = get_object_or_404(Movie, slug=slug, is_mobile_only=False)
        else:
            instance = self.get_object()
        serializer = self.get_serializer(instance)
        serialized_data = serializer.data
        # Fetch the authorization header
        auth_header = request.headers.get('Authorization', '')

        if isinstance(instance, (Movie, Series)):
            content_type = ContentType.objects.get_for_model(type(instance))
            all_comments = Comment.objects.filter(
                content_type=content_type, object_id=instance.id)

            comment_count = all_comments.count()

            top_level_comments = all_comments.filter(parent__isnull=True)
            comment_serializer = CommentSerializer(
                top_level_comments, many=True)
            serialized_data['comments'] = comment_serializer.data
            serialized_data['comment_count'] = comment_count

        # Determine if the content is free
        if isinstance(instance, Episode):
            # Accessing the series attributes from the episode
            is_free_content = instance.series.is_free
        else:

            is_free_content = instance.is_free

        # If no auth header is provided or the content is free, serve the content as it is
        if is_free_content:
            return standardResponse(status="success", message="Item retrieved", data=serialized_data)
        if auth_header.startswith('Bearer '):

            auth_status, user_info, _ = self.validate_token(request)
            print('user_info')
            # If the token is valid, check the user's subscription
            if auth_status and self.user_has_access_to_content(user_info['username'], instance):
                return standardResponse(status="success", message="Item retrieved", data=serialized_data)
        # For unauthenticated users or users without a valid subscription, hide the main content URL
        if isinstance(instance, Episode):
            serialized_data['episode_content_url'] = None
        else:
            serialized_data['main_content_url'] = None

        return standardResponse(status="success", message="Item retrieved", data=serialized_data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return standardResponse(status="success", message="Item updated", data=serializer.data)
        return standardResponse(status="error", message="Invalid data", data=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return standardResponse(status="success", message="Item deleted")

    def user_has_access_to_content(self, username, content):
        try:
            today = timezone.now().date()

            # Fetch subscriptions for the given username that are considered active
            # based on the status and the start and end dates.
            user_subs = UserSubscription.objects.filter(
                username=username,
                status='Active',
                start_date__lte=today,
                end_date__gte=today
            )
            all_subs = UserSubscription.objects.filter(username=username,status='Active')
            print(user_subs, all_subs)
            # Check if the subscri  ption is active
            if not user_subs.exists():
                return False

            # If the content is an episode, then get its parent series
            if isinstance(content, Episode):
                content_to_check = content.series
            else:
                content_to_check = content

            # Check if the content (movie/series) is available under the user's subscription plan
            for sub in user_subs:
                # Check if the content (movie/series) is available under the user's subscription plan
                if content_to_check.available_under_plans.filter(name=sub.subscription_plan_name).exists():
                    return True

            return False
        except UserSubscription.DoesNotExist:
            return False

    @action(detail=True, methods=['post'], url_path='add-favorite')
    def add_favorite(self, request, pk=None):
        content_type_request = request.data.get('content_type')
        try:
            # Validate the token and get user information
            auth_status, user_info, _ = self.validate_token(request)
            if not auth_status:
                return standardResponse(status='error', message='Invalid or expired token', data=status.HTTP_401_UNAUTHORIZED)

            # Fetch the content object based on type and ID
            if content_type_request == 'MOVIE':
                content_object = Movie.objects.get(pk=pk)
            elif content_type_request == 'SERIES':
                content_object = Series.objects.get(pk=pk)
            else:
                return standardResponse(status='error', message='Invalid content type', data=status.HTTP_400_BAD_REQUEST)

            # Get the content type for the content object
            content_type = ContentType.objects.get_for_model(
                content_object.__class__)

            # Check if the content is already a favorite
            existing_favorite = FavoriteContent.objects.filter(
                username=user_info['username'],
                content_type=content_type,
                object_id=content_object.pk
            )
            if existing_favorite.exists():
                return standardResponse(status='error', message='Content already added to favorites', data={"content_id": content_object.pk})

            # Create a new favorite content entry
            favorite = FavoriteContent.objects.create(
                username=user_info['username'],
                content_type=content_type,
                object_id=content_object.pk
            )
            return standardResponse(status='success', message='Added to favorites', data={"content_id": content_object.pk})

        except (Movie.DoesNotExist, Series.DoesNotExist):
            return standardResponse(status='error', message='Content not found', data=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return standardResponse(status='error', message=str(e), data=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'], url_path='remove-favorite')
    def remove_favorite(self, request, pk=None):
        content_type = request.data.get('content_type')
        try:
            auth_status, user_info, _ = self.validate_token(request)
            if not auth_status:
                return standardResponse(status='error', message='Invalid or expired token', data=status.HTTP_401_UNAUTHORIZED)

            # Fetch the content object based on type and ID
            if content_type == 'MOVIE':
                content_object = Movie.objects.get(pk=pk)
            elif content_type == 'SERIES':
                content_object = Series.objects.get(pk=pk)
            else:
                return standardResponse(status='error', message='Invalid content type', data=status.HTTP_400_BAD_REQUEST)

            content_type_model = ContentType.objects.get_for_model(
                content_object.__class__)

            favorite = FavoriteContent.objects.filter(
                username=user_info['username'],
                content_type=content_type_model,
                object_id=content_object.pk
            )
            if favorite.exists():
                favorite.delete()
                return standardResponse(status='success', message='Removed from favorites', data={"content_id": content_object.pk})
            else:
                return standardResponse(status='error', message='Favorite not found', data=status.HTTP_404_NOT_FOUND)

        except (Movie.DoesNotExist, Series.DoesNotExist):
            return standardResponse(status='error', message='Content not found', data=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return standardResponse(status='error', message=str(e), data=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MobileOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        is_mobile = self.is_request_from_mobile(request)
        if not is_mobile and self.get_queryset().filter(is_mobile_only=True).exists():
            return standardResponse(status='error', message='This content is only available on mobile devices.', data={})
        return super().dispatch(request, *args, **kwargs)

    def is_request_from_mobile(self, request):
        # Simple check. Can be enhanced based on User-Agent or custom headers
        user_agent = request.headers.get('User-Agent', '').lower()
        return 'mobile' in user_agent or 'dart' in user_agent


class MobileOnlyEpisodes:
    """
    Mixin to be used with viewsets to filter out episodes from series 
    that are marked as mobile only when the request is not from a mobile device.
    """

    def dispatch(self, request, *args, **kwargs):
        # Call the parent dispatch method to start with the standard processing
        response = super().dispatch(request, *args, **kwargs)

        # Apply additional filtering logic only for non-mobile requests
        if not self.is_request_from_mobile(request):
            # Get IDs of series marked as 'mobile only'
            mobile_only_series_ids = Series.objects.filter(
                is_mobile_only=True).values_list('id', flat=True)

            # Modify the queryset of the viewset to exclude these series
            self.queryset = self.queryset.exclude(
                series_id__in=mobile_only_series_ids)

        return response

    def is_request_from_mobile(self, request):
        # Implement logic to determine if the request is from a mobile device
        user_agent = request.headers.get('User-Agent', '').lower()
        return 'mobile' in user_agent
