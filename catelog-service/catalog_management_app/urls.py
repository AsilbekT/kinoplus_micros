from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FavoriteContentViewSetManagement, VideoConversionTypeViewSet, GenreViewSet,
                    DirectorViewSet, MovieViewSet, SeriesViewSetManagement, SeasonViewSet, EpisodeViewSet, BannerViewSet, CommentViewSet, CatagorySerializerViewSet, AdvancedSearch, AdvancedV2Search)

router2 = DefaultRouter()
router2.register(r'video-conversion-types', VideoConversionTypeViewSet)
router2.register(r'genres', GenreViewSet)
router2.register(r'directors', DirectorViewSet)
router2.register(r'movies', MovieViewSet)
router2.register(r'series', SeriesViewSetManagement)
router2.register(r'seasons', SeasonViewSet)
router2.register(r'catagory', CatagorySerializerViewSet)
router2.register(r'episodes', EpisodeViewSet)
router2.register(r'banners', BannerViewSet)
router2.register(r'comments', CommentViewSet)
router2.register(r'favorite-contents', FavoriteContentViewSetManagement)

urlpatterns = [
    path('', include("catalog_management_app.auth.urls")),
    path('search/', AdvancedSearch.as_view(), name='management_search'),
    path('v2/search/', AdvancedV2Search.as_view(), name='management_search'),

    path('', include(router2.urls)),
]
