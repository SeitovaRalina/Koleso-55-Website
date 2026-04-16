import django_filters
from .models import Excursion, Category
from django.db import models


class ExcursionFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category__slug',
        to_field_name='slug',
        label='Категория',
        help_text='Фильтр по категории экскурсии (используйте slug категории)'
    )

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Цена от')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Цена до')

    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte', label='Длительность от (мин)')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte', label='Длительность до (мин)')

    location_type = django_filters.ChoiceFilter(
        choices=Excursion.LocationType.choices,
        field_name='location_type',
        label='Тип локации'
    )

    search = django_filters.CharFilter(
        method='filter_search',
        label='Поиск'
    )

    date_from = django_filters.DateFilter(
        method='filter_date_from',
        label='Дата от'
    )

    class Meta:
        model = Excursion
        fields = []

    def filter_search(self, queryset, name, value):
        """Поиск по названию, краткому и полному описанию"""
        if not value:
            return queryset

        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(short_description__icontains=value) |
            models.Q(description__icontains=value)
        )

    def filter_date_from(self, queryset, name, value):
        """Только экскурсии, у которых есть хотя бы один доступный слот с датой >= value"""
        if not value:
            return queryset

        return queryset.filter(
            slots__date__gte=value,
            slots__available_seats__gt=0
        ).distinct()
