from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<slug:tour_slug>/', views.ReviewCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='delete'),
]