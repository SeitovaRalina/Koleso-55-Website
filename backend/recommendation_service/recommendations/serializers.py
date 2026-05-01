from rest_framework import serializers
from .models import User, Excursion, UserExcursion


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']


class ExcursionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excursion
        fields = ['id', 'title', 'description', 'short_description', 'location', 
                 'duration', 'price', 'created_at', 'is_active']


class UserExcursionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    excursion = ExcursionSerializer(read_only=True)

    class Meta:
        model = UserExcursion
        fields = ['id', 'user', 'excursion', 'visited_at']


class MarkVisitedSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID of the user")
    excursion_id = serializers.IntegerField(help_text="ID of the excursion")
