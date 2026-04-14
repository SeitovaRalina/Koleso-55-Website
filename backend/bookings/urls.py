from django.urls import path
from .views import TourOrderCreateView

app_name = 'bookings'

urlpatterns = [
    path('orders/', TourOrderCreateView.as_view(), name='order-create'),
]
