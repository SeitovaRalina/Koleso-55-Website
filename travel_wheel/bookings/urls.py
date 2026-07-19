from django.urls import path
from .views import (
    BookingListView,
    BookingDetailView,
    CreateBookingView,
    CancelBookingView
)

urlpatterns = [
    path("", BookingListView.as_view()),
    path("create/", CreateBookingView.as_view()),
    path("<int:pk>/", BookingDetailView.as_view()),
    path("<int:pk>/cancel/", CancelBookingView.as_view()),
]
