from typing import List, Optional
from datetime import datetime

from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_field
from drf_spectacular.types import OpenApiTypes
from excursions.models import Excursion
from excursions.serializers import ExcursionListSerializer
from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели избранного"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор записи в избранном",
        read_only=True
    )
    user = serializers.IntegerField(
        label="ID пользователя",
        help_text="Уникальный идентификатор пользователя",
        source='user.id',
        read_only=True
    )
    excursion = serializers.IntegerField(
        label="ID экскурсии",
        help_text="Уникальный идентификатор экскурсии"
    )
    added_at = serializers.DateTimeField(
        label="Дата добавления",
        help_text="Дата и время добавления в избранное",
        read_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'excursion', 'added_at']


class WishlistListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка избранного с деталями экскурсий"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор записи в избранном",
        read_only=True
    )
    excursion = ExcursionListSerializer(
        label="Экскурсия",
        help_text="Детальная информация об экскурсии"
    )
    added_at = serializers.DateTimeField(
        label="Дата добавления",
        help_text="Дата и время добавления в избранное",
        read_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'excursion', 'added_at']


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления экскурсии в избранное"""

    excursion = serializers.PrimaryKeyRelatedField(
        label="Экскурсия",
        help_text="ID экскурсии для добавления в избранное",
        queryset=Excursion.objects.filter(is_active=True),
    )

    class Meta:
        model = Wishlist
        fields = ['excursion']


class WishlistCheckSerializer(serializers.Serializer):
    """Сериализатор для проверки наличия экскурсии в избранном"""
    
    is_in_wishlist = serializers.BooleanField(
        label="В избранном",
        help_text="Флаг, указывающий на наличие экскурсии в избранном"
    )
