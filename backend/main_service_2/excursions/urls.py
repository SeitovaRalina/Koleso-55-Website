from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.create_user, name='create_user'),
    path('users/list/', views.get_users, name='get_users'),
    path('excursions/', views.add_excursion, name='add_excursion'),
    path('excursions/list/', views.get_excursions, name='get_excursions'),
    path('excursions/visited/', views.mark_visited, name='mark_visited'),
    path('users/<int:user_id>/excursions/', views.get_user_excursions, name='get_user_excursions'),
]
