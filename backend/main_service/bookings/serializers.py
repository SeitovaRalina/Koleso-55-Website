from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import TourOrder, ContactMethod


class TourOrderCreateSerializer(serializers.ModelSerializer):
    # Для гостевых пользователей
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    contact_method = serializers.CharField(required=False, default='call')
    
    # Для авторизованных пользователей
    save_to_profile = serializers.BooleanField(
        write_only=True, 
        default=True,
        help_text="Сохранить данные в профиль"
    )

    class Meta:
        model = TourOrder
        fields = [
            'id', 'excursion', 'slot', 'first_name', 'last_name', 'middle_name', 'phone', 'email',
            'num_participants', 'contact_method', 'comment', 'save_to_profile'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        slot = attrs['slot']
        num = attrs['num_participants']

        if not slot.is_available or slot.available_seats < num:
            raise serializers.ValidationError(
                {"slot": "В выбранном слоте недостаточно мест"}
            )

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Для авторизованных пользователей авто-заполнение из профиля
            user = request.user
            if not attrs.get('first_name'):
                attrs['first_name'] = user.first_name or ''
            if not attrs.get('last_name'):
                attrs['last_name'] = user.last_name or ''
            if not attrs.get('middle_name'):
                attrs['middle_name'] = getattr(user, 'middle_name', '') or ''
            if not attrs.get('phone'):
                attrs['phone'] = user.phone or ''
            if not attrs.get('email'):
                attrs['email'] = user.email or ''

        if attrs.get('contact_method') == ContactMethod.EMAIL and not attrs.get('email'):
            raise serializers.ValidationError(
                {"email": "При выборе Email необходимо указать адрес"}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        save_to_profile = validated_data.pop('save_to_profile', True)
        
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            
            # Если нужно сохранить данные в профиль
            if save_to_profile:
                user = request.user
                update_fields = []
                if validated_data.get('first_name') and not user.first_name:
                    user.first_name = validated_data['first_name']
                    update_fields.append('first_name')
                if validated_data.get('last_name') and not user.last_name:
                    user.last_name = validated_data['last_name']
                    update_fields.append('last_name')
                if validated_data.get('middle_name') and not getattr(user, 'middle_name', ''):
                    setattr(user, 'middle_name', validated_data['middle_name'])
                    # Не добавляем в update_fields, так как поля нет в модели
                # Не обновляем телефон через бронирование - только через профиль
                if update_fields:
                    user.save(update_fields=update_fields)
        else:
            # Для гостевых пользователей просто создаем заказ
            # Привязка к аккаунту произойдет позже при регистрации
            pass

        order = super().create(validated_data)
        return order

class TourOrderListSerializer(serializers.ModelSerializer):
    excursion_id = serializers.IntegerField(source='excursion.id', read_only=True)
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    excursion_slug = serializers.CharField(source='excursion.slug', read_only=True)
    slot_datetime = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contact_method_display = serializers.CharField(source='get_contact_method_display', read_only=True)

    class Meta:
        model = TourOrder
        fields = [
            'id', 'excursion_id', 'excursion_title', 'excursion_slug', 'slot_datetime', 'num_participants',
            'status', 'status_display', 'created_at', 'contact_method_display'
        ]

    @extend_schema_field(serializers.CharField())
    def get_slot_datetime(self, obj):
        return f"{obj.slot.date} {obj.slot.time}"


class TourOrderDetailSerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    excursion_slug = serializers.CharField(source='excursion.slug', read_only=True)
    slot_datetime = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contact_method_display = serializers.CharField(source='get_contact_method_display', read_only=True)

    class Meta:
        model = TourOrder
        fields = [
            'id', 'excursion_title', 'excursion_slug', 'slot_datetime',
            'first_name', 'last_name', 'phone', 'email',
            'num_participants', 'contact_method', 'contact_method_display',
            'email', 'comment', 'status', 'status_display',
            'manager_comment', 'created_at', 'updated_at'
        ]

    @extend_schema_field(serializers.CharField())
    def get_slot_datetime(self, obj):
        return f"{obj.slot.date} {obj.slot.time}"
