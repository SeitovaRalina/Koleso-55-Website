from django.urls import path
from .views import (
    GiftCertificateRequestCreateView,
    MyGiftCertificateRequestListView,
    CustomTourRequestCreateView,
    MyCustomTourRequestListView,
    TourOrderCreateView,
    MyOrdersListView,
    MyOrderDetailView,
    MyOrderCancelView,
)

app_name = 'bookings'

urlpatterns = [
    path('certificate-requests/', GiftCertificateRequestCreateView.as_view(), name='certificate-request-create'),
    path('my-certificate-requests/', MyGiftCertificateRequestListView.as_view(), name='my-certificate-request-list'),
    path('custom-tour-requests/', CustomTourRequestCreateView.as_view(), name='custom-tour-request-create'),
    path('my-custom-tour-requests/', MyCustomTourRequestListView.as_view(), name='my-custom-tour-request-list'),
    path('orders/', TourOrderCreateView.as_view(), name='order-create'),

    path('my-orders/', MyOrdersListView.as_view(), name='my-orders-list'),
    path('my-orders/<int:pk>/', MyOrderDetailView.as_view(), name='my-order-detail'),
    path('my-orders/<int:pk>/cancel/', MyOrderCancelView.as_view(), name='my-order-cancel'),
]
