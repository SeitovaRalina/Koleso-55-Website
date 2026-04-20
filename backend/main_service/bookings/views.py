from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers

from .models import TourOrder, OrderStatus
from .serializers import (
    TourOrderCreateSerializer,
    TourOrderListSerializer,
    TourOrderDetailSerializer,
)

class TourOrderCreateView(generics.CreateAPIView):
    serializer_class = TourOrderCreateSerializer
    permission_classes = [permissions.AllowAny]

class MyOrdersListView(generics.ListAPIView):
    serializer_class = TourOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TourOrder.objects.none()
        return TourOrder.objects.filter(
            user=self.request.user
        ).select_related('excursion', 'slot').order_by('-created_at')

class MyOrderDetailView(generics.RetrieveAPIView):
    serializer_class = TourOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TourOrder.objects.none()
        return TourOrder.objects.filter(
            user=self.request.user
        ).select_related('excursion', 'slot')

class MyOrderCancelView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.Serializer

    def post(self, request, pk):
        try:
            order = TourOrder.objects.get(pk=pk, user=request.user)
        except TourOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден или не принадлежит вам."}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in (OrderStatus.NEW, OrderStatus.CONFIRMED):
            return Response(
                {"detail": "Можно отменить только заказы со статусом 'Новый' или 'Подтверждён'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = OrderStatus.CANCELLED
        order.save()

        return Response({"message": "Заказ успешно отменён."}, status=status.HTTP_200_OK)
