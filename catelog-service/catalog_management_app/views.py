from rest_framework import viewsets
from video_app.models import (
    Banner, Catagory, Comment,
    Director, Episode, FavoriteContent,
    Season, Series, Genre,
    Movie, VideoConversionType
)
from .serializers import (
    BannerSerializer, CatagorySerializer,
    CommentSerializer, DirectorSerializer,
    EpisodeSerializer, FavoriteContentPlanSerializer,
    SeasonSerializer, SeriesSerializer,
    GenreSerializer, MovieSerializer,
    VideoConversionTypeSerializer
)
from video_app.utils import paginate_queryset

from video_app.utils import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .decorators import check_authorization_header 
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination

@method_decorator(check_authorization_header, name='dispatch')
class CatagorySerializerViewSet(viewsets.ModelViewSet):
    queryset = Catagory.objects.all().order_by("id")
    serializer_class = CatagorySerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated, IsAdminOrSuperuser]
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Catagiries retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Catagiries successfully deleted", data={})


@method_decorator(check_authorization_header, name='dispatch')
class FavoriteContentViewSetManagement(viewsets.ModelViewSet):
    queryset = FavoriteContent.objects.all().order_by("id")
    serializer_class = FavoriteContentPlanSerializer
    # authentication_classes = [JWTAuthentication]  # JWT Authentication
    # permission_classes = [IsAuthenticated]  # Permission class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Favirute Content retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Favorite content successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class VideoConversionTypeViewSet(viewsets.ModelViewSet):
    queryset = VideoConversionType.objects.all().order_by("id")
    serializer_class = VideoConversionTypeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Video Conversion retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Video conversion successfully deleted", data={})


@method_decorator(check_authorization_header, name='dispatch')
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by("id")
    serializer_class = GenreSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Genres retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Genre successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Director.objects.all().order_by("id")
    serializer_class = DirectorSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Directors retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Director successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Movies retrieved", data=serializer.data, pagination=pagination_data)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Movie successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class SeriesViewSetManagement(viewsets.ModelViewSet):
    queryset = Series.objects.all().order_by("id")
    serializer_class = SeriesSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Series retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Series successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all().order_by("id")
    serializer_class = SeasonSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Seasons retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Seoson successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all().order_by("id")
    serializer_class = EpisodeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Episodes retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Episode successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all().order_by("id")
    serializer_class = BannerSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Banners retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Banner content successfully deleted", data={})

@method_decorator(check_authorization_header, name='dispatch')
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("id")
    serializer_class = CommentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginated_queryset, pagination_data = paginate_queryset(
            queryset, request)
        if not paginated_queryset:
            return standardResponse(status="success", message="No content found", data={})

        serializer = self.get_serializer(
            paginated_queryset, many=True, context={'request': request})
        return standardResponse(status="success", message="Comments retrieved", data=serializer.data, pagination=pagination_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return standardResponse(status="success", message="Comment successfully deleted", data={})



# from django.db.models.functions import ExtractYear
# from django.contrib.sites.shortcuts import get_current_site
# from rest_framework.views import APIView
# from video_app.models import Movie, Series
# from video_app.utils import standardResponse, paginate_queryset
# from video_app.serializers import HomeMovieSerializer, HomeSeriesSerializer
# from django.db.models import Q


# class AdvancedSearch(APIView):
#     def get(self, request):
#         # Search and filtering parameters
#         query = request.GET.get('q', '')
#         genre = request.GET.get('genre', '')
#         director = request.GET.get('director', '')
#         min_rating = request.GET.get('min_rating', None)
#         max_rating = request.GET.get('max_rating', None)
#         start_year = request.GET.get('start_year', None)
#         end_year = request.GET.get('end_year', None)

#         # Building the query for movies and series
#         movie_query = Q(title__icontains=query)
#         series_query = Q(title__icontains=query)


#         if genre:
#             movie_query &= Q(genre__name__icontains=genre)
#             series_query &= Q(genre__name__icontains=genre)

#         if director:
#             movie_query &= Q(director__name__icontains=director)
#             series_query &= Q(director__name__icontains=director)

#         if min_rating:
#             movie_query &= Q(rating__gte=min_rating)
#             series_query &= Q(rating__gte=min_rating)

#         if max_rating:
#             movie_query &= Q(rating__lte=max_rating)
#             series_query &= Q(rating__lte=max_rating)

#         if start_year:
#             try:
#                 start_year = int(start_year)
#                 movie_query &= Q(release_date__year__gte=start_year)
#                 series_query &= Q(release_date__year__gte=start_year)
#             except ValueError:
#                 # Handle invalid start_year value
#                 pass

#         if end_year:
#             try:
#                 end_year = int(end_year)
#                 movie_query &= Q(release_date__year__lte=end_year)
#                 series_query &= Q(release_date__year__lte=end_year)
#             except ValueError:
#                 # Handle invalid end_year value
#                 pass

#         # Fetching results
#         movies = Movie.objects.filter(movie_query).distinct()
#         series = Series.objects.filter(series_query).distinct()

#         # Combining and paginating results
#         combined_results = list(movies) + list(series)
#         paginated_results, pagination_data = paginate_queryset(
#             combined_results, request)

#         # Serialize the data
#         data_list = [{
#             "id": item.id,
#             "title": item.title,
#             "type": "Movie" if isinstance(item, Movie) else "Series",
#             "release_date": item.release_date,
#             "genre": [genre.name for genre in item.genre.all()],
#             "director": item.director.name,
#             "thumbnail_image": self.build_absolute_uri(item.thumbnail_image.url) if item.thumbnail_image else None,
#             "rating": item.rating
#         } for item in paginated_results]
#         return standardResponse(status="success", message="Data fetched successfully", data={"content": data_list, "pagination": pagination_data})

#     def build_absolute_uri(self, relative_url):
#         current_site = get_current_site(self.request)
#         absolute_url = 'https://' + current_site.domain + relative_url
#         return absolute_url


# class AvailableYearsView(APIView):
#     def get(self, request):
#         movie_years = Movie.objects.filter(is_ready=True).annotate(year=ExtractYear(
#             'release_date')).values_list('year', flat=True).distinct()
#         series_years = Series.objects.filter(is_ready=True).annotate(year=ExtractYear(
#             'release_date')).values_list('year', flat=True).distinct()
#         combined_years = set(list(movie_years) + list(series_years))
#         available_years = sorted(list(combined_years))

#         data = {
#             "available_years": available_years
#         }
#         return standardResponse(status="success", message="Data fetched successfully", data=data)



# class AdvancedSearchSecondVersion(APIView):
#     def get(self, request):
#         # Search and filtering parameters
#         category = request.GET.get('category', '')
#         query = request.GET.get('q', '')
#         genre = request.GET.get('genre', '')
#         director = request.GET.get('director', '')
#         min_rating = request.GET.get('min_rating', None)
#         max_rating = request.GET.get('max_rating', None)
#         start_year = request.GET.get('start_year', None)
#         end_year = request.GET.get('end_year', None)


#         movie_query = Q(title__icontains=query)
#         series_query = Q(title__icontains=query)

from django.db.models.functions import ExtractYear
from django.contrib.sites.shortcuts import get_current_site
from video_app.utils import standardResponse, paginate_queryset
from video_app.serializers import HomeMovieSerializer, HomeSeriesSerializer
from django.db.models import Q
from rest_framework.views import APIView

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Adjust the number of items per page as needed
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdvancedSearch(APIView):
    def get(self, request):
        # Search and filtering parameters
        category = request.GET.get('category', '')
        query = request.GET.get('q', '')
        genre = request.GET.get('genre', '')
        director = request.GET.get('director', '')
        min_rating = request.GET.get('min_rating', None)
        max_rating = request.GET.get('max_rating', None)
        start_year = request.GET.get('start_year', None)
        end_year = request.GET.get('end_year', None)

        # Building the query for movies and series
        movie_query = Q(title__icontains=query)
        series_query = Q(title__icontains=query)

        if category:
            category_ids = Catagory.objects.filter(id=category)
            movie_query &= Q(category_id__in=category_ids)
            series_query &= Q(category_id__in=category_ids)

        if genre:
            movie_query &= Q(genre__name__icontains=genre)
            series_query &= Q(genre__name__icontains=genre)

        if director:
            movie_query &= Q(director__name__icontains=director)
            series_query &= Q(director__name__icontains=director)

        if min_rating:
            movie_query &= Q(rating__gte=min_rating)
            series_query &= Q(rating__gte=min_rating)

        if max_rating:
            movie_query &= Q(rating__lte=max_rating)
            series_query &= Q(rating__lte=max_rating)

        if start_year:
            try:
                start_year = int(start_year)
                movie_query &= Q(release_date__year__gte=start_year)
                series_query &= Q(release_date__year__gte=start_year)
            except ValueError:
                # Handle invalid start_year value
                pass

        if end_year:
            try:
                end_year = int(end_year)
                movie_query &= Q(release_date__year__lte=end_year)
                series_query &= Q(release_date__year__lte=end_year)
            except ValueError:
                # Handle invalid end_year value
                pass

        # Fetching results
        movies = Movie.objects.filter(movie_query).distinct()
        series = Series.objects.filter(series_query).distinct()

        # Combining and paginating results
        combined_results = list(movies) + list(series)
        paginated_results, pagination_data = paginate_queryset(
            combined_results, request)

        # Serialize the data
        data_list = [{
            "id": item.id,
            "title": item.title,
            "type": "Movie" if isinstance(item, Movie) else "Series",
            "release_date": item.release_date,
            "genre": [{"id": genre.id, "name": genre.name} for genre in item.genre.all()],
            "director": item.director.name,
            "thumbnail_image": self.build_absolute_uri(item.thumbnail_image.url) if item.thumbnail_image else None,
            "rating": item.rating,
            "is_premiere": item.is_premiere 
        } for item in paginated_results]

        return standardResponse(status="success", message="Data fetched successfully", data={"content": data_list, "pagination": pagination_data})

    def build_absolute_uri(self, relative_url):
        current_site = get_current_site(self.request)
        absolute_url = 'https://' + current_site.domain + relative_url
        return absolute_url


class AdvancedSearchSecondVersion(APIView):
    def get(self, request):
        # Search and filtering parameters
        category = request.GET.get('category', '')
        query = request.GET.get('q', '')
        genre = request.GET.get('genre', '')
        director = request.GET.get('director', '')
        min_rating = request.GET.get('min_rating', None)
        max_rating = request.GET.get('max_rating', None)
        start_year = request.GET.get('start_year', None)
        end_year = request.GET.get('end_year', None)

        # Building the query for movies and series
        movie_query = Q(title__icontains=query)
        series_query = Q(title__icontains=query)

        if category:
            category_ids = Catagory.objects.filter(id=category)
            movie_query &= Q(category_id__in=category_ids)
            series_query &= Q(category_id__in=category_ids)

        if genre:
            movie_query &= Q(genre__name__icontains=genre)
            series_query &= Q(genre__name__icontains=genre)

        if director:
            movie_query &= Q(director__name__icontains=director)
            series_query &= Q(director__name__icontains=director)

        if min_rating:
            movie_query &= Q(rating__gte=min_rating)
            series_query &= Q(rating__gte=min_rating)

        if max_rating:
            movie_query &= Q(rating__lte=max_rating)
            series_query &= Q(rating__lte=max_rating)

        if start_year:
            try:
                start_year = int(start_year)
                movie_query &= Q(release_date__year__gte=start_year)
                series_query &= Q(release_date__year__gte=start_year)
            except ValueError:
                # Handle invalid start_year value
                pass

        if end_year:
            try:
                end_year = int(end_year)
                movie_query &= Q(release_date__year__lte=end_year)
                series_query &= Q(release_date__year__lte=end_year)
            except ValueError:
                # Handle invalid end_year value
                pass

        movies = Movie.objects.filter(movie_query).distinct()
        series = Series.objects.filter(series_query).distinct()

        # Combining and paginating results
        combined_results = list(movies) + list(series)
        paginated_results, pagination_data = paginate_queryset(combined_results, request)

        # Serialize the data
        content_list = []
        for item in paginated_results:
            if isinstance(item, Movie):
                serialized_item = HomeMovieSerializer(item, context={'request': request}).data
                serialized_item['is_movie'] = True
            else:
                serialized_item = HomeSeriesSerializer(item, context={'request': request}).data
                serialized_item['is_movie'] = False
            content_list.append(serialized_item)

        # Return standard response with custom pagination
        return standardResponse(status="success", message="Data fetched successfully", data={"content": content_list, "pagination": pagination_data})



class AvailableYearsView(APIView):
    def get(self, request):
        movie_years = Movie.objects.filter(is_ready=True).annotate(year=ExtractYear(
            'release_date')).values_list('year', flat=True).distinct()
        series_years = Series.objects.filter(is_ready=True).annotate(year=ExtractYear(
            'release_date')).values_list('year', flat=True).distinct()
        combined_years = set(list(movie_years) + list(series_years))
        available_years = sorted(list(combined_years))

        data = {
            "available_years": available_years
        }
        return standardResponse(status="success", message="Data fetched successfully", data=data)


class AdvancedV2Search(APIView):
    def get(self, request):
        # Basic search and filtering parameters
        content_ids = request.GET.get('id', '')
        if content_ids:
            content_id_list = [int(id) for id in content_ids.split(',') if id.isdigit()]
        else:
            return Response({"status": "error", "message": "No IDs provided"})

        # Initialize queries for movies, series, and episodes
        movie_query = Q(id__in=content_id_list, is_ready=True)
        series_query = Q(id__in=content_id_list, is_ready=True)
        episode_query = Q(id__in=content_id_list, is_ready=True)

        # Fetching results based on the IDs
        movies = Movie.objects.filter(movie_query).distinct()
        series = Series.objects.filter(series_query).distinct()
        episodes = Episode.objects.filter(episode_query).distinct()

        # Combine results
        combined_results = list(movies) + list(series) + list(episodes)

        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_results = paginator.paginate_queryset(combined_results, request, view=self)
        
        # Serialize the paginated data
        data_list = []
        for item in paginated_results:
            item_data = {
                "id": item.id,
                "title": item.title,
                "type": "Movie" if isinstance(item, Movie) else "Series" if isinstance(item, Series) else "Episode",
                "release_date": item.release_date if not isinstance(item, Episode) else None,
                "rating": item.rating if not isinstance(item, Episode) else item.series.rating,
                "is_premiere": item.is_premiere if not isinstance(item, Episode) else item.series.is_premiere,
            }
            if isinstance(item, Episode):
                item_data["thumbnail_image"] = self.build_absolute_uri(item.thumbnail_image_url.url) if item.thumbnail_image_url else None

            if isinstance(item, Movie) or isinstance(item, Series):
                item_data["genre"] = [{"id": genre.id, "name": genre.name} for genre in item.genre.all()]
                item_data["director"] = item.director.name if item.director else None
                item_data["thumbnail_image"] = self.build_absolute_uri(item.thumbnail_image.url) if item.thumbnail_image else None
            
            data_list.append(item_data)

        # Return the paginated response
        return paginator.get_paginated_response(data_list)

    def build_absolute_uri(self, relative_url):
        current_site = get_current_site(self.request)
        absolute_url = 'https://' + current_site.domain + relative_url
        return absolute_url