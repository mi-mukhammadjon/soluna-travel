from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    path('', views.RegionListView.as_view(), name='region-list'),
    path('<slug:slug>/', views.RegionDetailView.as_view(), name='region-detail'),
]