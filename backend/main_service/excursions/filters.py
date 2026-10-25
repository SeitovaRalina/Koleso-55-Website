import django_filters
from django.db import models
from django.db.models import Exists, OuterRef, Q

from .models import Excursion, Slot


DURATION_BUCKETS = {
    "under_2h": Q(duration__lt=120),
    "2_to_4h": Q(duration__gte=120, duration__lte=240),
    "over_4h": Q(duration__gt=240),
}


class ExcursionFilter(django_filters.FilterSet):
    # The multi-value fields are applied together in filter_queryset. A regular
    # CharFilter or ChoiceFilter silently keeps only the last repeated value.
    category = django_filters.CharFilter(method="passthrough", label="Категория")
    location_type = django_filters.CharFilter(method="passthrough", label="Тип локации")
    duration = django_filters.CharFilter(method="passthrough", label="Диапазон длительности")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="gte")
    max_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")
    date_from = django_filters.DateFilter(method="passthrough")
    date_to = django_filters.DateFilter(method="passthrough")
    ids = django_filters.BaseInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = Excursion
        fields = []

    def passthrough(self, queryset, name, value):
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value)
            | models.Q(short_description__icontains=value)
            | models.Q(description__icontains=value)
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if "category" in self.data:
            categories = self.data.getlist("category")
            queryset = queryset.filter(category__slug__in=categories) if all(categories) else queryset.none()
        if "location_type" in self.data:
            locations = self.data.getlist("location_type")
            valid = set(Excursion.LocationType.values)
            queryset = queryset.filter(location_type__in=locations) if locations and all(v in valid for v in locations) else queryset.none()
        if "duration" in self.data:
            durations = self.data.getlist("duration")
            if durations and all(v in DURATION_BUCKETS for v in durations):
                condition = Q()
                for duration in durations:
                    condition |= DURATION_BUCKETS[duration]
                queryset = queryset.filter(condition)
            else:
                queryset = queryset.none()

        start = self.form.cleaned_data.get("date_from")
        end = self.form.cleaned_data.get("date_to")
        if start or end:
            if start and end and start > end:
                return queryset.none()
            slots = Slot.objects.filter(excursion_id=OuterRef("pk"))
            if start:
                slots = slots.filter(date__gte=start)
            if end:
                slots = slots.filter(date__lte=end)
            queryset = queryset.filter(Exists(slots))
        return queryset
