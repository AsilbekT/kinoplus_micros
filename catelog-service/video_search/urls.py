from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.AdvancedSearch.as_view(), name='general_search'),
    path('v2/searchTelegram/', views.AdvancedSearchTelegram.as_view(), name='telegram_search'),
    path('v2/search/', views.AdvancedSearchSecondVersion.as_view(), name='v2_general_search'),
    path('v2/searchSlugTelegram/', views.SlugSearchTelegram.as_view(),
         name='slug-search'),
    path('available-years/', views.AvailableYearsView.as_view(),
         name='available-years'),
]
