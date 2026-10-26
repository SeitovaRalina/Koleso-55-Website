from django.contrib import admin

from .models import NewsArticle, NewsBlock, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class NewsBlockInline(admin.StackedInline):
    model = NewsBlock
    extra = 1
    min_num = 1
    validate_min = True
    fields = ('position', 'kind', 'text', 'image', 'alt', 'caption')
    show_change_link = False


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'is_published')
    list_filter = ('is_published', 'category', 'published_at')
    search_fields = ('title', 'excerpt', 'body', 'blocks__text')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    fields = ('title', 'slug', 'excerpt', 'cover', 'category', 'published_at', 'is_published')
    inlines = (NewsBlockInline,)
