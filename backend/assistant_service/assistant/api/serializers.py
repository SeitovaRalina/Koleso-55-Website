from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(max_length=2000, required=True)

class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    answer = serializers.CharField()
    is_booking_intent = serializers.BooleanField()