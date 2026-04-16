from rest_framework import serializers
from .models import Review, ReviewImage, ReviewStatus
from .services.profanity_filter import toxicity_filter


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']


class ReviewCreateSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = ['excursion', 'rating', 'text', 'images']

    def validate(self, attrs):
        request = self.context['request']
        excursion = attrs['excursion']

        has_completed_order = request.user.orders.filter(
            excursion=excursion,
            status='completed'
        ).exists()

        if not has_completed_order:
            raise serializers.ValidationError(
                "Оставить отзыв можно только после посещения экскурсии (статус заказа «Выполнен»)."
            )

        check = toxicity_filter.is_toxic(attrs['text'])

        attrs['is_toxic'] = check['is_toxic']
        attrs['toxicity_score'] = check['score']

        if check['is_toxic']:
            attrs['status'] = ReviewStatus.REJECTED
        else:
            attrs['status'] = ReviewStatus.PENDING

        return attrs


class ReviewListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'text', 'images', 'created_at']
