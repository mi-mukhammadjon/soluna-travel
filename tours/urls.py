from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.TourListView.as_view(), name='tour-list'),
    path('api/filter/', views.tour_filter_api, name='tour-filter-api'),
    path('<int:pk>/wishlist/', views.wishlist_toggle, name='wishlist-toggle'),
    path('<slug:slug>/', views.TourDetailView.as_view(), name='tour-detail'),
]