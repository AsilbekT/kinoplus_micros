from django.urls import path, include
from .views import *

urlpatterns = [
    path("megogo/", GetPopularMegagoFilms.as_view()),
    path("megogo/content/details/", GetContentDetailsMegago.as_view())
]
