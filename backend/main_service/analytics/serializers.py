from rest_framework import serializers
from .models import ExcursionView
from excursions.models import Excursion


class ExcursionViewStartSerializer(serializers.ModelSerializer):
    excursion_id = serializers.IntegerField(write_only=True)
    session_id = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = ExcursionView
        fields = ['excursion_id', 'session_id', 'source']
    
    def validate_excursion_id(self, value):
        if not Excursion.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Экскурсия не найдена или неактивна")
        return value


class ExcursionViewHeartbeatSerializer(serializers.Serializer):
    view_id = serializers.IntegerField()
    elapsed_seconds = serializers.IntegerField(min_value=1)


class ExcursionViewEndSerializer(serializers.Serializer):
    view_id = serializers.IntegerField()


class ExcursionViewSerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ExcursionView
        fields = [
            'id', 'user', 'user_email', 'excursion', 'excursion_title',
            'session_id', 'duration_seconds', 'source', 'started_at',
            'processed_for_recommendations'
        ]
        read_only_fields = ['id', 'user', 'duration_seconds', 'started_at', 'processed_for_recommendations']
