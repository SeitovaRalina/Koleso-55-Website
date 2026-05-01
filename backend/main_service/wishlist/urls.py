from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.WishlistListView.as_view(), name='wishlist-list'),
    path('add/', views.WishlistCreateView.as_view(), name='wishlist-add'),
    path('<int:excursion_id>/', views.WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('check/<int:excursion_id>/', views.check_wishlist, name='wishlist-check'),
]
