from django.urls import path
from .views import ReviewCreateView, ReviewListView, ReviewUpdateView, MyReviewsListView

urlpatterns = [
    path('excursions/<int:excursion_id>/reviews/', ReviewListView.as_view(), name='review-list'),
    path('', ReviewCreateView.as_view(), name='review-create'),
    path('<int:pk>/', ReviewUpdateView.as_view(), name='review-update'),      # редактирование
    path('my-reviews/', MyReviewsListView.as_view(), name='my-reviews'),             # мои отзывы
]
