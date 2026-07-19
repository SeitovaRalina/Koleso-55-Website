from django.urls import path

from .views import (
    HomepageReviewListView,
    MyReviewsListView,
    ReviewCreateView,
    ReviewListView,
    ReviewUpdateView,
)


urlpatterns = [
    path('excursions/<int:excursion_id>/reviews/', ReviewListView.as_view(), name='review-list'),
    path('homepage/', HomepageReviewListView.as_view(), name='homepage-reviews'),
    path('my-reviews/', MyReviewsListView.as_view(), name='my-reviews'),
    path('', ReviewCreateView.as_view(), name='review-create'),
    path('<int:pk>/', ReviewUpdateView.as_view(), name='review-update'),
]
