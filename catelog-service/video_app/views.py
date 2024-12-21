from django.contrib.contenttypes.models import ContentType
from video_app.utils import decode_token, standardResponse, user_has_active_plan
from .models import Catagory, Comment, Content, FavoriteContent, Genre, Director, Movie, Season, Series, Episode, Banner, SubscriptionPlan, UserSubscription, ContentType, VideoConversionType, PandaDocs
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    EpisodeSerializerDetails,
    FavoriteContentSerializer,
    GenreSerializer,
    DirectorSerializer,
    HomeMovieSerializer,
    MovieDetailSerializer,
    MovieSerializer,
    SeasonSerializer,
    SeasonWithEpisodesSerializer,
    SeriesDetailSerializer,
    SeriesListSerializer,
    SeriesSerializer,
    EpisodeSerializer,
    BannerSerializer,
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    VideoConversionTypeSerializer,
    ContentTypeBannerSerializer,
    PandaDocsSerializer,
    EpisodeSerializerWithoutContent
)
from .base_view import BaseViewSet, MobileOnlyMixin, MobileOnlyEpisodes
from video_app.utils import paginate_queryset
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Subquery, OuterRef
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
import logging
logger = logging.getLogger(__name__)

class VideoConversionTypeListView(BaseViewSet):
    queryset = VideoConversionType.objects.all()
    serializer_class = VideoConversionTypeSerializer

class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class DirectorViewSet(BaseViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer

class MovieFeaturedViewSet(MobileOnlyMixin, BaseViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieSerializer

    def list(self, request, *args, **kwargs):
        try:

            # Fetch movies and series related to this category
            movies = Movie.objects.filter(is_featured=True).order_by('id')
            series = Series.objects.filter(is_featured=True).order_by('id')
            # Combine movies and series into a single queryset
            combined_content = list(movies) + list(series)

            # Paginate the combined list using your custom function
            paginated_queryset, pagination_data = paginate_queryset(
                combined_content, request)
            if not paginated_queryset:
                return standardResponse(status="success", message="Content not found.", data=[])

            # Serialize page items
            content_list = []
            for item in paginated_queryset:
                if isinstance(item, Movie):
                    serialized_item = HomeMovieSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = True
                else:
                    serialized_item = SeriesListSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = False

                serialized_item['telegram_link'] = item.telegram_link
                serialized_item['slug'] = item.slug
                serialized_item['telegram_private_channel'] = item.telegram_private_channel
                content_list.append(serialized_item)

            # Return standard response with custom pagination
            return standardResponse(status="success", message="Contents retrieved", data={"content": content_list, "pagination": pagination_data})

        except Exception as e:
            return standardResponse(status="error", message=str(e), data={})


class MovieViewSet(MobileOnlyMixin, BaseViewSet):
    serializer_class = MovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.filter(is_ready=True)
        if not self.is_request_from_mobile(self.request):
            queryset = queryset.filter(is_mobile_only=False)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieSerializer

    def list(self, request, *args, **kwargs):
        genre_from_param = request.query_params.get('genre', None)
        queryset = self.get_queryset().filter(
            genre_id=genre_from_param) if genre_from_param else self.get_queryset()

        # Ensure the queryset is ordered
        # or any other field you want to order by
        queryset = queryset.order_by('id')

        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="error", message="Invalid page.", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Movies retrieved", data=serializer.data, pagination=pagination_data)


class SeriesViewSet(MobileOnlyMixin, BaseViewSet):
    serializer_class = SeriesSerializer

    def get_queryset(self):
        queryset = Series.objects.filter(is_ready=True).order_by('id')
        
        # Use DRF's query_params if available, otherwise fallback to Django's GET
        genre_from_param = self.request.query_params.get('genre', None) if hasattr(self.request, 'query_params') else self.request.GET.get('genre', None)

        if not self.is_request_from_mobile(self.request):
            queryset = queryset.filter(is_mobile_only=False)

        if genre_from_param:
            queryset = queryset.filter(genre_id=genre_from_param)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return SeriesListSerializer  # For listing series with only necessary fields
        elif self.action == 'retrieve':
            return SeriesDetailSerializer  # For detailed view of a single series
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="error", message="Invalid page.", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Series retrieved", data=serializer.data, pagination=pagination_data)

class EpisodeViewSet(MobileOnlyEpisodes, BaseViewSet):
    queryset = Episode.objects.all().order_by('series', 'season', 'episode_number')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EpisodeSerializer
        elif self.action == 'retrieve':
            return EpisodeSerializerDetails
        return EpisodeSerializer

    def list(self, request, *args, **kwargs):
        auth_status, user_info, _ = self.validate_token(request)

        series_id = kwargs.get('series_pk', None)
        season_id = kwargs.get('season_pk', None)

        queryset = self.queryset.filter(is_ready=True)
        if series_id:
            queryset = queryset.filter(series_id=series_id)
        if season_id:
            queryset = queryset.filter(season_id=season_id)

        # Use the first episode for access check if specific series or season is requested
        content_instance_for_access_check = queryset.first() if series_id or season_id else None
 
        paginated_queryset, pagination_data = paginate_queryset(queryset, request)
        if not paginated_queryset:
            return standardResponse(status="error", message="Invalid page.", data={})
        if not content_instance_for_access_check.series.is_free:
           
            if auth_status:
                # Use the access check to determine which serializer to use
                if content_instance_for_access_check and self.user_has_access_to_content(user_info['username'], content_instance_for_access_check):
                    serializer = EpisodeSerializer(paginated_queryset, many=True, context={'request': request})
                else:
                    # User doesn't have an active subscription or content instance is None
                    serializer = EpisodeSerializerWithoutContent(paginated_queryset, many=True, context={'request': request})
            else:
                # For unauthenticated users or users without a valid token, use a serializer that excludes sensitive content
                serializer = EpisodeSerializerWithoutContent(paginated_queryset, many=True, context={'request': request})
        else:
            serializer = EpisodeSerializer(paginated_queryset, many=True, context={'request': request})
            
        return standardResponse(status="success", message="Episodes retrieved", data={'episodes': serializer.data, 'pagination': pagination_data})


class SeasonViewSet(BaseViewSet):
    queryset = Season.objects.all().order_by('season_number')
    serializer_class = SeasonSerializer

    def get_queryset(self):
        """
        This view should return a list of all seasons
        for the series as determined by the series portion of the URL.
        """
        # Extract series_id from URL parameters
        series_id = self.kwargs.get('series_pk')  # 'series_pk' should match the lookup field defined in your router

        if series_id is not None:
            # Filter queryset by the extracted series_id
            queryset = Season.objects.filter(series_id=series_id).order_by('season_number')
            if not queryset.exists():
                # Raise an HTTP 404 error if no seasons are found for the given series
                raise NotFound(detail="No seasons found for the specified series.", code=404)
            return queryset
        else:
            raise NotFound(detail="Series ID not specified.", code=404)
            
    def get_serializer_class(self):
        if self.action == 'list':
            return SeasonSerializer
        elif self.action == 'retrieve':
            return SeasonWithEpisodesSerializer
        return SeasonSerializer


class CategoryViewSet(BaseViewSet):
    serializer_class = CategorySerializer
    queryset = Catagory.objects.none()

    def get_cached_content(self, pk):
        cache_key = f'category_content_{pk}'
        return cache.get(cache_key)

    def cache_content(self, pk, data, timeout=3600):
        cache_key = f'category_content_{pk}'
        cache.set(cache_key, data, timeout=timeout)


    def list(self, request, *args, **kwargs):
        try:
            categories = Catagory.objects.filter(is_active=True).order_by("priority")
            category_serializer = CategorySerializer(
                categories, many=True, context={'request': request})

            # Aggregate data
            data = {
                "categories": category_serializer.data,
            }

            return standardResponse(status="success", message="Data retrieved", data=data)
        except Exception as e:
            return standardResponse(status="error", message=str(e), data={})

    @action(detail=True, methods=['GET'])
    def content(self, request, pk=None):
        # cache_key = f'category_{pk}_content'
        # cached_content = cache.get(cache_key)

        try:
            category = Catagory.objects.get(id=pk)

            # Fetch movies and series related to this category
            movies = Movie.objects.filter(category=category, is_ready=True).order_by('id')
            series = Series.objects.filter(category=category, is_ready=True).order_by('id')
            # Combine movies and series into a single queryset
            combined_content = list(movies) + list(series)

            # Paginate the combined list using your custom function
            paginated_queryset, pagination_data = paginate_queryset(
                combined_content, request)
            if not paginated_queryset:
                return standardResponse(status="error", message="Invalid page.", data={})

            # Serialize page items
            content_list = []
            for item in paginated_queryset:
                if isinstance(item, Movie):
                    serialized_item = HomeMovieSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = True
                else:
                    serialized_item = SeriesListSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = False
                content_list.append(serialized_item)

            # Return standard response with custom pagination
            return standardResponse(status="success", message="Contents retrieved", data={"content": content_list, "pagination": pagination_data})

        except Catagory.DoesNotExist:
            return standardResponse(status="error", message="Category not found", data={})
        except Exception as e:
            return standardResponse(status="error", message=str(e), data={})

    @action(detail=False, methods=['get'], url_path='(?P<slug>[^/.]+)')
    def slug(self, request, slug=None, **kwargs):
        try:
            category = Catagory.objects.get(slug=slug)

            # Fetch movies and series related to this category
            movies = Movie.objects.filter(category=category, is_ready=True).order_by('id')
            series = Series.objects.filter(category=category, is_ready=True).order_by('id')
            # Combine movies and series into a single queryset
            combined_content = list(movies) + list(series)

            # Paginate the combined list using your custom function
            paginated_queryset, pagination_data = paginate_queryset(
                combined_content, request)
            if not paginated_queryset:
                return standardResponse(status="error", message="Invalid page.", data={})

            # Serialize page items
            content_list = []
            for item in paginated_queryset:
                if isinstance(item, Movie):
                    serialized_item = HomeMovieSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = True
                else:
                    serialized_item = SeriesListSerializer(
                        item, context={'request': request}).data
                    serialized_item['is_movie'] = False
                content_list.append(serialized_item)

            # Return standard response with custom pagination
            return standardResponse(status="success", message="Contents retrieved", data={"content": content_list, "pagination": pagination_data})

        except Catagory.DoesNotExist:
            return standardResponse(status="error", message="Category not found", data={})
        except Exception as e:
            return standardResponse(status="error", message=str(e), data={})

class BannerViewSet(BaseViewSet):
    queryset = Banner.objects.filter(status=True)
    serializer_class = BannerSerializer


class SubscriptionPlanView(BaseViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by("-id")
    serializer_class = SubscriptionPlanSerializer



class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all().order_by('-start_date')
    serializer_class = UserSubscriptionSerializer

    def update(self, request, *args, **kwargs):
        print(kwargs)
        username = kwargs.get('username')
        subscription_plan_name = kwargs.get('subscription_plan_name')

        # Log the parameters received
        logger.info(f"Updating subscription for username: {username}, plan: {subscription_plan_name}")

        try:
            instance = UserSubscription.objects.get(username=username, subscription_plan_name=subscription_plan_name)
        except UserSubscription.DoesNotExist:
            # Log the error and the available instances
            logger.error(f"Subscription not found for username: {username}, plan: {subscription_plan_name}")
            logger.debug(f"Available subscriptions: {UserSubscription.objects.all()}")
            return standardResponse(status="error", message="Subscription not found", data={})

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            # Sync updated subscription with catalog service
            return standardResponse(status="success", message="Item updated", data=serializer.data)
        return standardResponse(status="error", message="Invalid data", data=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('username')
        subscription_plan_name = kwargs.get('subscription_plan_name')

        # Log the parameters received
        logger.info(f"Deleting subscription for username: {username}, plan: {subscription_plan_name}")

        try:
            instance = UserSubscription.objects.filter(username=username, subscription_plan_name=subscription_plan_name)
        except UserSubscription.DoesNotExist:
            # Log the error and the available instances
            logger.error(f"Subscription not found for username: {username}, plan: {subscription_plan_name}")
            logger.debug(f"Available subscriptions: {UserSubscription.objects.all()}")
            return standardResponse(status="error", message="Subscription not found", data={})

        instance.delete()
        # Sync deletion with catalog service
        return standardResponse(status="success", message="Item deleted", data={})

class FavoriteContentViewSet(BaseViewSet):
    queryset = FavoriteContent.objects.all()
    serializer_class = FavoriteContentSerializer
    

    def list(self, request, *args, **kwargs):
        # Validate the token
        auth_status, user_info, _ = self.validate_token(request)
        if not auth_status:
            return standardResponse(status='error', message='Invalid or expired token', data=status.HTTP_401_UNAUTHORIZED)

        # Fetch favorite movies and series
        favorite_content = FavoriteContent.objects.filter(
            username=user_info['username'])
        movie_ids = favorite_content.filter(content_type=ContentType.objects.get_for_model(
            Movie)).values_list('object_id', flat=True)
        series_ids = favorite_content.filter(content_type=ContentType.objects.get_for_model(
            Series)).values_list('object_id', flat=True)

        # Query movies and series
        movies_query = Movie.objects.filter(id__in=movie_ids).order_by("id")
        series_query = Series.objects.filter(id__in=series_ids).order_by("id")
        # Combine movies and series into a single queryset
        combined_content = list(movies_query) + list(series_query)

        # Paginate the combined list using your custom function
        paginated_queryset, pagination_data = paginate_queryset(
            combined_content, request)
        if not paginated_queryset:
            return standardResponse(status="error", message="Invalid page.", data={})

        # Serialize page items
        content_list = []
        for item in paginated_queryset:
            if isinstance(item, Movie):
                serialized_item = HomeMovieSerializer(
                    item, context={'request': request}).data
                serialized_item['is_movie'] = True
            else:
                serialized_item = SeriesListSerializer(
                    item, context={'request': request}).data
                serialized_item['is_movie'] = False
            content_list.append(serialized_item)

        # Return standard response with custom pagination
        return standardResponse(status="success", message="Contents retrieved", data={"content": content_list, "pagination": pagination_data})


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        content_type_str = self.request.data.get('content_type', '').lower()
        object_id = self.request.data.get('object_id')

        if not content_type_str or not object_id:
            return standardResponse('error', 'Missing content type or object ID', {}, status.HTTP_400_BAD_REQUEST)

        app_label = 'video_app'  # Replace with your actual app label

        try:
            content_type = ContentType.objects.get(
                app_label=app_label, model=content_type_str)
        except ContentType.DoesNotExist:
            return standardResponse('error', 'Invalid content type', {}, status.HTTP_400_BAD_REQUEST)

        username = self.get_username_from_token()
        serializer.save(username=username,
                        content_type=content_type, object_id=object_id)

    def get_username_from_token(self):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '').split()
        if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
            token = auth_header[1]
            user_info = decode_token(token)
            return user_info.get('username', 'anonymous')
        return 'anonymous'

    def create(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
            return standardResponse('error', 'Invalid or expired token', {}, status.HTTP_401_UNAUTHORIZED)

        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            return standardResponse('success', 'Comment created', response.data)
        return response

    def get_queryset(self):
        content_type_str = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type_str and object_id:
            app_label = 'video_app'  # Replace with your actual app label
            try:
                content_type = ContentType.objects.get(
                    app_label=app_label, model=content_type_str.lower())
                return Comment.objects.filter(content_type=content_type, object_id=object_id)
            except ContentType.DoesNotExist:
                pass  # Handle the exception as needed

        return Comment.objects.none()


class ContentTypeListView(BaseViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeBannerSerializer


class PandaDocsView(BaseViewSet):
    queryset = PandaDocs.objects.all()
    serializer_class = PandaDocsSerializer
