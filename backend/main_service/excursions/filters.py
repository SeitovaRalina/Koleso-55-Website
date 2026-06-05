import django_filters
from django.db import models

from .models import Excursion


class ExcursionFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__slug",
        label="Категория",
        help_text="Фильтр по категории экскурсии. Используйте slug категории.",
        method="filter_category",
    )

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Цена от")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Цена до")

    min_duration = django_filters.NumberFilter(
        field_name="duration",
        lookup_expr="gte",
        label="Длительность от (мин)",
    )
    max_duration = django_filters.NumberFilter(
        field_name="duration",
        lookup_expr="lte",
        label="Длительность до (мин)",
    )

    location_type = django_filters.ChoiceFilter(
        choices=Excursion.LocationType.choices,
        field_name="location_type",
        label="Тип локации",
    )

    search = django_filters.CharFilter(
        method="filter_search",
        label="Поиск",
    )

    date_from = django_filters.DateFilter(
        method="filter_date_from",
        label="Дата от",
    )

    date_to = django_filters.DateFilter(
        method="filter_date_to",
        label="Дата до",
    )

    class Meta:
        model = Excursion
        fields = []

    def filter_category(self, queryset, name, value):
        """Фильтрация по одной или нескольким категориям."""
        if not value:
            return queryset

        # Логирование для отладки
        print(f"filter_category called with value: {value}, type: {type(value)}")

        # Если value - это список (несколько категорий)
        if isinstance(value, list):
            return queryset.filter(category__slug__in=value).distinct()

        # Если value - это строка (одна категория)
        return queryset.filter(category__slug=value).distinct()

    def filter_search(self, queryset, name, value):
        """Поиск по названию, краткому и полному описанию."""
        if not value:
            return queryset

        return queryset.filter(
            models.Q(title__icontains=value)
            | models.Q(short_description__icontains=value)
            | models.Q(description__icontains=value)
        )

    def filter_date_from(self, queryset, name, value):
        """Только экскурсии, у которых есть хотя бы один слот с датой >= value."""
        if not value:
            return queryset

        # Временно упрощаем - просто фильтруем по дате слота
        return queryset.filter(slots__date__gte=value).distinct()

    def filter_date_to(self, queryset, name, value):
        """Только экскурсии, у которых есть хотя бы один слот с датой <= value."""
        if not value:
            return queryset

        return queryset.filter(slots__date__lte=value).distinct()
