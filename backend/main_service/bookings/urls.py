from django.urls import path
from .views import (
    GiftCertificateRequestCreateView,
    TourOrderCreateView,
    MyOrdersListView,
    MyOrderDetailView,
    MyOrderCancelView,
)

app_name = 'bookings'

urlpatterns = [
    path('certificate-requests/', GiftCertificateRequestCreateView.as_view(), name='certificate-request-create'),
    path('orders/', TourOrderCreateView.as_view(), name='order-create'),

    path('my-orders/', MyOrdersListView.as_view(), name='my-orders-list'),
    path('my-orders/<int:pk>/', MyOrderDetailView.as_view(), name='my-order-detail'),
    path('my-orders/<int:pk>/cancel/', MyOrderCancelView.as_view(), name='my-order-cancel'),
]
