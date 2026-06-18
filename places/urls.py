from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('nearby/', views.NearbyPlacesAPIView.as_view(), name='nearby'),
    path('attraction/<int:attraction_id>/nearby/', views.AttractionNearbyView.as_view(), name='attraction-nearby'),
]