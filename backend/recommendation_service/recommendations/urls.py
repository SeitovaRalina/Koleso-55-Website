from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/<int:user_id>/', views.get_recommendations, name='get_recommendations'),
    path('health/', views.health_check, name='health_check'),
    path('users/', views.list_users, name='list_users'),
    path('excursions/', views.list_excursions, name='list_excursions'),
    path('excursions/visited/', views.mark_visited, name='mark_visited'),
    path('users/<int:user_id>/visited/', views.get_user_visited_excursions, name='get_user_visited_excursions'),
]
