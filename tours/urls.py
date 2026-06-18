from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.TourListView.as_view(), name='tour-list'),
    path('<slug:slug>/', views.TourDetailView.as_view(), name='tour-detail'),
]