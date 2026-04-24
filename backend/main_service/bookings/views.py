from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import OrderStatus, TourOrder
from .serializers import (
    TourOrderCreateSerializer,
    TourOrderDetailSerializer,
    TourOrderListSerializer,
)


@extend_schema(
    summary="Создание заказа на экскурсию",
    description="Создает новый заказ на экскурсию. Доступно как для авторизованных, так и для неавторизованных пользователей. "
                   "Проверяет доступность слота и корректность данных. Автоматически создает пользователя если указаны email/телефон.",
)
class TourOrderCreateView(generics.CreateAPIView):
    serializer_class = TourOrderCreateSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    summary="Список заказов пользователя",
    description="Возвращает список всех заказов текущего пользователя с возможностью фильтрации по статусу. "
                   "Заказы отсортированы по дате создания (новые первые). Требует JWT токен доступа.",
)
class MyOrdersListView(generics.ListAPIView):
    serializer_class = TourOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TourOrder.objects.none()
        return (
            TourOrder.objects.filter(user=self.request.user)
            .select_related("excursion", "slot")
            .order_by("-created_at")
        )


@extend_schema(
    summary="Детальная информация о заказе",
    description="Возвращает полную информацию о конкретном заказе текущего пользователя. "
                   "Включает все детали экскурсии, слота, контактной информации и историю изменений. "
                   "Требует JWT токен доступа.",
)
class MyOrderDetailView(generics.RetrieveAPIView):
    serializer_class = TourOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TourOrder.objects.none()
        return TourOrder.objects.filter(user=self.request.user).select_related("excursion", "slot")


class OrderCancelResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorDetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class MyOrderCancelView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderCancelResponseSerializer

    @extend_schema(
        summary="Отмена заказа",
        description="Отменяет заказ текущего пользователя. Доступно только для заказов со статусом 'Новый' или 'Подтверждён'. "
                       "После отмены заказ нельзя восстановить. Требует JWT токен доступа.",
    )
    def post(self, request, pk):
        try:
            order = TourOrder.objects.get(pk=pk, user=request.user)
        except TourOrder.DoesNotExist:
            return Response(
                {"detail": "Заказ не найден или не принадлежит вам."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status not in (OrderStatus.NEW, OrderStatus.CONFIRMED):
            return Response(
                {"detail": "Можно отменить только заказы со статусом 'Новый' или 'Подтверждён'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = OrderStatus.CANCELLED
        order.save()

        return Response(
            {"message": "Заказ успешно отменён."},
            status=status.HTTP_200_OK,
        )
