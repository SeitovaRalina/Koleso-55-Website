from django.urls import path
from .views import ReviewCreateView, ReviewListView

app_name = 'reviews'

urlpatterns = [
    path('excursions/<int:excursion_id>/reviews/', ReviewListView.as_view(), name='review-list'),
    path('', ReviewCreateView.as_view(), name='review-create'),
]
