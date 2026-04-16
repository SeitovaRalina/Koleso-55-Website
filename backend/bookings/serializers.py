from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import TourOrder, ContactMethod


class TourOrderCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = TourOrder
        fields = [
            'excursion', 'slot', 'first_name', 'last_name', 'phone', 'email',
            'num_participants', 'contact_method', 'email', 'comment'
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
            user = request.user
            attrs.setdefault('first_name', user.first_name)
            attrs.setdefault('last_name', user.last_name)
            attrs.setdefault('phone', user.phone)
            attrs.setdefault('email', user.email)

        if attrs.get('contact_method') == ContactMethod.EMAIL and not attrs.get('email'):
            raise serializers.ValidationError(
                {"email": "При выборе Email необходимо указать адрес"}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

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
