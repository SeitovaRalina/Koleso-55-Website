from typing import List, Optional
from decimal import Decimal
from datetime import date, time

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Excursion, Category, ExcursionImage, Slot, ExcursionProgramDay, TicketType, ExcursionInquiry
from reviews.serializers import ReviewListSerializer


class ExcursionInquirySerializer(serializers.ModelSerializer):
    request_id = serializers.UUIDField(required=True)
    excursion = serializers.PrimaryKeyRelatedField(queryset=Excursion.objects.filter(is_active=True))
    name = serializers.CharField(max_length=120, allow_blank=False, trim_whitespace=True)
    question = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    phone = serializers.RegexField(r'^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$', max_length=18, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = ExcursionInquiry
        fields = ['request_id', 'excursion', 'name', 'phone', 'email', 'contact_method', 'question']

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Укажите имя не короче 2 символов.')
        return value

    def validate_question(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Укажите вопрос не короче 5 символов.')
        return value

    def validate(self, attrs):
        if attrs['contact_method'] == ExcursionInquiry.ContactMethod.EMAIL:
            if not attrs.get('email'):
                raise serializers.ValidationError({'email': 'Укажите email для связи.'})
        elif not attrs.get('phone'):
            raise serializers.ValidationError({'phone': 'Укажите телефон для выбранного способа связи.'})
        return attrs


class MyExcursionInquirySerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    public_status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExcursionInquiry
        fields = ['id', 'excursion', 'excursion_title', 'question', 'created_at', 'public_status']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий экскурсий"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор категории",
        read_only=True
    )
    name = serializers.CharField(
        label="Название",
        help_text="Название категории экскурсий",
        max_length=100
    )
    slug = serializers.SlugField(
        label="Slug",
        help_text="URL-совместимое название категории",
        max_length=120,
        read_only=True
    )
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ExcursionImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображений экскурсий"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор изображения",
        read_only=True
    )
    image = serializers.ImageField(
        label="Изображение",
        help_text="Фотография экскурсии",
        use_url=True
    )
    alt_text = serializers.CharField(
        label="Alt-текст",
        help_text="Альтернативный текст для изображения",
        max_length=200,
        required=False,
        allow_blank=True
    )
    is_main = serializers.BooleanField(
        label="Главное фото",
        help_text="Является ли изображение главным для экскурсии",
        default=False
    )
    
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'alt_text', 'is_main']


class SlotSerializer(serializers.ModelSerializer):
    """Сериализатор слотов (временных интервалов) экскурсий"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор слота",
        read_only=True
    )
    date = serializers.DateField(
        label="Дата",
        help_text="Дата проведения экскурсии"
    )
    time = serializers.TimeField(
        label="Время начала",
        help_text="Время начала экскурсии"
    )
    end_date = serializers.DateField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    max_participants = serializers.IntegerField(
        label="Макс. участников",
        help_text="Максимальное количество участников"
    )
    available_seats = serializers.IntegerField(
        label="Доступно мест",
        help_text="Количество свободных мест",
        read_only=True
    )
    is_available = serializers.BooleanField(
        label="Доступен",
        help_text="Доступен ли слот для бронирования",
        read_only=True
    )
    price_override = serializers.DecimalField(
        label="Цена для слота",
        help_text="Особая цена для этого слота (если отличается от базовой)",
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Slot
        fields = [
            'id', 'date', 'time', 'end_date', 'end_time', 'max_participants',
            'available_seats', 'is_available', 'price_override'
        ]

    def validate(self, attrs):
        start_date = attrs.get('date', getattr(self.instance, 'date', None))
        start_time = attrs.get('time', getattr(self.instance, 'time', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if (end_date is None) != (end_time is None):
            raise serializers.ValidationError('Укажите дату и время окончания вместе.')
        if end_date and (end_date, end_time) <= (start_date, start_time):
            raise serializers.ValidationError('Окончание должно быть позже начала.')
        return attrs


class ExcursionProgramDaySerializer(serializers.ModelSerializer):
    """Сериализатор дней программы для многодневных туров"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор дня программы",
        read_only=True
    )
    day_number = serializers.IntegerField(
        label="Номер дня",
        help_text="Порядковый номер дня в туре"
    )
    title = serializers.CharField(
        label="Заголовок дня",
        help_text="Название или тема дня",
        max_length=200
    )
    description = serializers.CharField(
        label="Описание программы дня",
        help_text="Подробное описание программы на этот день"
    )

    class Meta:
        model = ExcursionProgramDay
        fields = ['id', 'day_number', 'title', 'description']


class TicketTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типов билетов"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор типа билета",
        read_only=True
    )
    name = serializers.CharField(
        label="Название типа",
        help_text="Например: Взрослый, Детский, Студенческий",
        max_length=50
    )
    price = serializers.DecimalField(
        label="Цена",
        help_text="Цена билета данного типа",
        max_digits=10,
        decimal_places=2
    )
    is_active = serializers.BooleanField(
        label="Активен",
        help_text="Доступен ли данный тип билета для бронирования"
    )

    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'is_active']


class ExcursionListSerializer(serializers.ModelSerializer):
    """Сериализатор списка экскурсий"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор экскурсии",
        read_only=True
    )
    title = serializers.CharField(
        label="Название",
        help_text="Название экскурсии",
        max_length=200
    )
    slug = serializers.SlugField(
        label="Slug",
        help_text="URL-совместимое название экскурсии",
        max_length=250,
        read_only=True
    )
    short_description = serializers.CharField(
        label="Краткое описание",
        help_text="Краткое описание экскурсии (до 500 символов)",
        max_length=500
    )
    location_type_display = serializers.CharField(
        label="Тип локации",
        help_text="Отображаемое название типа локации",
        source='get_location_type_display',
        read_only=True
    )
    price = serializers.DecimalField(
        label="Цена от",
        help_text="Минимальная цена участия в экскурсии",
        max_digits=10,
        decimal_places=2
    )
    duration = serializers.IntegerField(
        label="Длительность",
        help_text="Длительность экскурсии в минутах"
    )
    category = CategorySerializer(
        label="Категория",
        help_text="Категория, к которой относится экскурсия",
        read_only=True
    )
    main_image = serializers.SerializerMethodField(
        label="Главное изображение",
        help_text="URL главного изображения экскурсии"
    )
    average_rating = serializers.SerializerMethodField(
        label="Средний рейтинг",
        help_text="Средний рейтинг на основе одобренных отзывов"
    )
    review_count = serializers.SerializerMethodField(
        label="Количество отзывов",
        help_text="Количество одобренных отзывов"
    )

    nearest_slots = serializers.SerializerMethodField()
    ticket_types = TicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'short_description',
            'location_type_display', 'price', 'duration', 'category', 'main_image',
            'average_rating', 'review_count', 'nearest_slots', 'ticket_types', 'is_multi_day'
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first() or obj.images.first()
        return main.image.url if main else None

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_average_rating(self, obj):
        """Средний рейтинг только по одобренным отзывам"""
        from django.db.models import Avg
        avg = obj.reviews.filter(status='approved').aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else None

    @extend_schema_field(serializers.IntegerField())
    def get_review_count(self, obj):
        """Количество одобренных отзывов"""
        return obj.reviews.filter(status='approved').count()

    @extend_schema_field(SlotSerializer(many=True))
    def get_nearest_slots(self, obj):
        slots = obj.slots.filter(date__gte=timezone.localdate()).order_by('date', 'time')[:3]
        return SlotSerializer(slots, many=True).data


class ExcursionDetailSerializer(serializers.ModelSerializer):
    """Сериализатор детальной информации об экскурсии"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор экскурсии",
        read_only=True
    )
    title = serializers.CharField(
        label="Название",
        help_text="Название экскурсии",
        max_length=200
    )
    slug = serializers.SlugField(
        label="Slug",
        help_text="URL-совместимое название экскурсии",
        max_length=250,
        read_only=True
    )
    description = serializers.CharField(
        label="Полное описание",
        help_text="Подробное описание экскурсии"
    )
    short_description = serializers.CharField(
        label="Краткое описание",
        help_text="Краткое описание экскурсии (до 500 символов)",
        max_length=500
    )
    price = serializers.DecimalField(
        label="Цена от",
        help_text="Минимальная цена участия в экскурсии",
        max_digits=10,
        decimal_places=2
    )
    duration = serializers.IntegerField(
        label="Длительность",
        help_text="Длительность экскурсии в минутах"
    )
    category = CategorySerializer(
        label="Категория",
        help_text="Категория, к которой относится экскурсия",
        read_only=True
    )
    location_type_display = serializers.CharField(
        label="Тип локации",
        help_text="Отображаемое название типа локации",
        source='get_location_type_display',
        read_only=True
    )
    tour_format_display = serializers.CharField(
        label="Формат поездки",
        help_text="Отображаемое название формата поездки",
        source='get_tour_format_display',
        read_only=True
    )
    group_size = serializers.IntegerField(
        label="Размер группы",
        help_text="Максимальное количество человек в группе"
    )
    is_multi_day = serializers.BooleanField(
        label="Многодневный тур",
        help_text="Является ли экскурсия многодневным туром"
    )
    included_in_price = serializers.CharField(
        label="Что входит в стоимость",
        help_text="Перечень услуг, включенных в стоимость",
        allow_blank=True,
        required=False
    )
    not_included_in_price = serializers.CharField(
        label="Что не входит в стоимость",
        help_text="Перечень услуг, не включенных в стоимость",
        allow_blank=True,
        required=False
    )
    what_to_bring = serializers.CharField(
        label="Что взять с собой",
        help_text="Рекомендации по вещам и экипировке",
        allow_blank=True,
        required=False
    )
    meeting_point = serializers.CharField(
        label="Место встречи",
        help_text="Место сбора группы",
        allow_blank=True,
        required=False,
        max_length=500
    )
    departure_time = serializers.TimeField(
        label="Время отправления",
        help_text="Время начала экскурсии",
        allow_null=True,
        required=False
    )
    images = ExcursionImageSerializer(
        label="Изображения",
        help_text="Все изображения экскурсии",
        many=True,
        read_only=True
    )
    slots = SlotSerializer(
        label="Слоты",
        help_text="Доступные временные слоты для бронирования",
        many=True,
        read_only=True
    )
    is_active = serializers.BooleanField(
        label="Активна",
        help_text="Доступна ли экскурсия для бронирования"
    )
    approved_reviews = serializers.SerializerMethodField(
        label="Одобренные отзывы",
        help_text="Список одобренных отзывов (максимум 10)"
    )
    average_rating = serializers.SerializerMethodField(
        label="Средний рейтинг",
        help_text="Средний рейтинг на основе одобренных отзывов"
    )
    review_count = serializers.SerializerMethodField(
        label="Количество отзывов",
        help_text="Количество одобренных отзывов"
    )
    rating_distribution = serializers.SerializerMethodField(
        label="Распределение оценок",
        help_text="Распределение отзывов по звёздам"
    )
    program_days = ExcursionProgramDaySerializer(
        label="Программа по дням",
        help_text="Программа для многодневных туров",
        many=True,
        read_only=True
    )
    ticket_types = TicketTypeSerializer(
        label="Типы билетов",
        help_text="Доступные типы билетов",
        many=True,
        read_only=True
    )

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'duration', 'category', 'location_type_display', 'tour_format_display',
            'group_size', 'is_multi_day', 'included_in_price', 'not_included_in_price',
            'what_to_bring', 'meeting_point', 'departure_time', 'images', 'slots', 'is_active',
            'approved_reviews', 'average_rating', 'review_count', 'rating_distribution',
            'program_days', 'ticket_types'
        ]

    @extend_schema_field(ReviewListSerializer(many=True))
    def get_approved_reviews(self, obj):
        """Только одобренные отзывы, отсортированные по новизне"""
        reviews = obj.reviews.filter(status='approved').order_by('-created_at')[:10]
        return ReviewListSerializer(reviews, many=True).data

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_average_rating(self, obj):
        """Средний рейтинг экскурсии"""
        from django.db.models import Avg
        avg = obj.reviews.filter(status='approved').aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    @extend_schema_field(serializers.IntegerField())
    def get_review_count(self, obj):
        """Количество одобренных отзывов"""
        return obj.reviews.filter(status='approved').count()

    @extend_schema_field(serializers.DictField())
    def get_rating_distribution(self, obj):
        """Распределение отзывов по звёздам"""
        from django.db.models import Count
        distribution = obj.reviews.filter(status='approved').values('rating').annotate(
            count=Count('id')
        ).order_by('rating')
        
        result = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for item in distribution:
            result[item['rating']] = item['count']
        
        return result


class ExcursionInternalSerializer(serializers.ModelSerializer):
    """Сериализатор экскурсий для внутреннего API (микросервис рекомендаций)"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор экскурсии",
        read_only=True
    )
    title = serializers.CharField(
        label="Название",
        help_text="Название экскурсии",
        max_length=200
    )
    description = serializers.CharField(
        label="Полное описание",
        help_text="Подробное описание экскурсии"
    )
    short_description = serializers.CharField(
        label="Краткое описание",
        help_text="Краткое описание экскурсии для превью",
        max_length=500
    )
    category = serializers.CharField(
        label="Категория",
        help_text="Название категории",
        source='category.name',
        read_only=True
    )
    location_type = serializers.CharField(
        label="Тип локации",
        help_text="Тип местоположения проведения экскурсии"
    )
    price = serializers.DecimalField(
        label="Цена от",
        help_text="Минимальная цена участия в экскурсии",
        max_digits=10,
        decimal_places=2
    )
    duration = serializers.IntegerField(
        label="Длительность",
        help_text="Продолжительность экскурсии в минутах"
    )
    created_at = serializers.DateTimeField(
        label="Дата создания",
        help_text="Дата и время создания экскурсии",
        read_only=True
    )
    updated_at = serializers.DateTimeField(
        label="Дата обновления",
        help_text="Дата и время последнего обновления экскурсии",
        read_only=True
    )

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'description', 'short_description',
            'category', 'location_type', 'price', 'duration',
            'created_at', 'updated_at'
        ]
