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
#         movie_query = Q(title__icontains=query) & Q(is_ready=True)
#         series_query = Q(title__icontains=query) & Q(is_ready=True)


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


#         movie_query = Q(title__icontains=query) & Q(is_ready=True)
#         series_query = Q(title__icontains=query) & Q(is_ready=True)

from django.db.models.functions import ExtractYear
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from video_app.models import Movie, Series, Catagory
from video_app.utils import standardResponse, paginate_queryset
from video_app.serializers import HomeMovieSerializer, HomeSeriesSerializer
from django.db.models import Q


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
        movie_query = Q(title__icontains=query) & Q(is_ready=True)
        series_query = Q(title__icontains=query) & Q(is_ready=True)

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
            "is_premiere": item.is_premiere,
            "is_mobile_only": item.is_mobile_only,
            "slug": item.slug 
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
        year = request.GET.get('year', '')
        director = request.GET.get('director', '')
        min_rating = request.GET.get('min_rating', None)
        max_rating = request.GET.get('max_rating', None)
        start_year = request.GET.get('start_year', None)
        end_year = request.GET.get('end_year', None)

        # Building the query for movies and series
        movie_query = Q(title__icontains=query) & Q(is_ready=True)
        series_query = Q(title__icontains=query) & Q(is_ready=True)

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

class AdvancedSearchTelegram(APIView):
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
        movie_query = Q(title__icontains=query) & Q(is_ready=True)
        series_query = Q(title__icontains=query) & Q(is_ready=True)

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
            serialized_item['telegram_link'] = item.telegram_link
            serialized_item['telegram_private_channel'] = item.telegram_private_channel
            # serialized_item['widescreen_thumbnail_image'] = item.widescreen_thumbnail_image
            content_list.append(serialized_item)

        # Return standard response with custom pagination
        return standardResponse(status="success", message="Data fetched successfully", data={"content": content_list, "pagination": pagination_data})


class SlugSearchTelegram(APIView):
    def get(self, request):
        # Search and filtering parameters
        slug = request.GET.get('slug', '')

        movie_query = Q(slug__icontains=slug) & Q(is_ready=True)
        series_query = Q(slug__icontains=slug) & Q(is_ready=True)

        movies = Movie.objects.filter(movie_query).distinct()
        series = Series.objects.filter(series_query).distinct()

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
            serialized_item['telegram_link'] = item.telegram_link
            # serialized_item['widescreen_thumbnail_image'] = item.widescreen_thumbnail_image
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
