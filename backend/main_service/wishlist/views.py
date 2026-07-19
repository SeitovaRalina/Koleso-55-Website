from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Wishlist
from .serializers import (
    WishlistCheckSerializer,
    WishlistCreateSerializer,
    WishlistListSerializer,
    WishlistSerializer,
)
from analytics.services import publish_recommendation_event


@extend_schema(
    summary="Получение списка избранного",
    description="Возвращает список всех экскурсий, добавленных текущим пользователем в избранное.",
)
class WishlistListView(generics.ListAPIView):
    """Получение списка избранного для текущего пользователя."""

    serializer_class = WishlistListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related("excursion__category")
            .prefetch_related("excursion__images")
        )


@extend_schema(
    summary="Добавление экскурсии в избранное",
    description="Добавляет указанную экскурсию в избранное текущего пользователя.",
)
class WishlistCreateView(generics.CreateAPIView):
    """Добавление экскурсии в избранное."""

    serializer_class = WishlistCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        wishlist = serializer.save(user=self.request.user)
        publish_recommendation_event(
            event_type="favorite",
            user_id=self.request.user.id,
            excursion_id=wishlist.excursion_id,
            source="direct",
        )


@extend_schema(
    summary="Удаление из избранного",
    description="Удаляет экскурсию из избранного текущего пользователя.",
)
class WishlistDeleteView(generics.DestroyAPIView):
    """Удаление экскурсии из избранного."""

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        excursion_id = self.kwargs["excursion_id"]
        try:
            return Wishlist.objects.get(
                user=self.request.user,
                excursion_id=excursion_id,
            )
        except Wishlist.DoesNotExist:
            return None

    def delete(self, request, *args, **kwargs):
        wishlist_item = self.get_object()
        if not wishlist_item:
            return Response(
                {"detail": "Экскурсия не найдена в избранном."},
                status=status.HTTP_404_NOT_FOUND,
            )

        wishlist_item.delete()
        return Response(
            {"detail": "Экскурсия удалена из избранного."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    summary="Проверка наличия в избранном",
    description="Проверяет, добавлена ли указанная экскурсия в избранное текущего пользователя.",
    responses={200: WishlistCheckSerializer},
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def check_wishlist(request, excursion_id):
    """Проверка наличия экскурсии в избранном."""

    is_in_wishlist = Wishlist.objects.filter(
        user=request.user,
        excursion_id=excursion_id,
    ).exists()

    serializer = WishlistCheckSerializer({"is_in_wishlist": is_in_wishlist})
    return Response(serializer.data)
