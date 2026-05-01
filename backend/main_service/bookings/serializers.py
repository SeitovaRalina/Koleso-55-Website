from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import TourOrder, ContactMethod


class TourOrderCreateSerializer(serializers.ModelSerializer):
    # Для гостевых пользователей
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    # Для авторизованных пользователей
    save_to_profile = serializers.BooleanField(
        write_only=True, 
        default=True,
        help_text="Сохранить данные в профиль"
    )

    class Meta:
        model = TourOrder
        fields = [
            'excursion', 'slot', 'first_name', 'last_name', 'middle_name', 'phone', 'email',
            'num_participants', 'contact_method', 'comment', 'save_to_profile'
        ]

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
            attrs.setdefault('first_name', user.first_name)
            attrs.setdefault('last_name', user.last_name)
            attrs.setdefault('middle_name', user.middle_name)
            attrs.setdefault('phone', user.phone)
            attrs.setdefault('email', user.email)

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
                if validated_data.get('first_name') and not user.first_name:
                    user.first_name = validated_data['first_name']
                if validated_data.get('last_name') and not user.last_name:
                    user.last_name = validated_data['last_name']
                if validated_data.get('middle_name') and not user.middle_name:
                    user.middle_name = validated_data['middle_name']
                if validated_data.get('phone') and not user.phone:
                    user.phone = validated_data['phone']
                user.save()
        else:
            # Для гостевых пользователей просто создаем заказ
            # Привязка к аккаунту произойдет позже при регистрации
            pass

        order = super().create(validated_data)
        return order

class TourOrderListSerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    slot_datetime = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contact_method_display = serializers.CharField(source='get_contact_method_display', read_only=True)

    class Meta:
        model = TourOrder
        fields = [
            'id', 'excursion_title', 'slot_datetime', 'num_participants',
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
