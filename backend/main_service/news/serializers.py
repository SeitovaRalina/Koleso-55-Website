from rest_framework import serializers

from .models import NewsArticle, NewsBlock, NewsCategory


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ('name', 'slug')


class NewsBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsBlock
        fields = ('kind', 'text', 'image', 'alt', 'caption', 'position')


class NewsArticleSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)

    class Meta:
        model = NewsArticle
        fields = ('title', 'slug', 'excerpt', 'cover', 'category', 'published_at')


class NewsArticleDetailSerializer(NewsArticleSerializer):
    blocks = NewsBlockSerializer(many=True, read_only=True)

    class Meta(NewsArticleSerializer.Meta):
        fields = NewsArticleSerializer.Meta.fields + ('blocks',)
