from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import NewsArticle, NewsBlock, NewsCategory


def article(slug, **kwargs):
    return NewsArticle.objects.create(
        title=slug, slug=slug, excerpt='Анонс', body='Полный текст', **kwargs
    )


class NewsApiTests(APITestCase):
    def test_only_published_and_due_articles_in_date_order(self):
        old = article('old', is_published=True, published_at=timezone.now() - timedelta(days=1))
        recent = article('recent', is_published=True)
        article('draft')
        article('future', is_published=True, published_at=timezone.now() + timedelta(days=1))

        response = self.client.get(reverse('news:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual([item['slug'] for item in response.data['results']], [recent.slug, old.slug])
        self.assertNotIn('body', response.data['results'][0])

    def test_detail_hides_draft_and_future_article(self):
        article('published', is_published=True)
        article('draft')
        article('future', is_published=True, published_at=timezone.now() + timedelta(days=1))
        self.assertEqual(self.client.get(reverse('news:detail', args=['published'])).status_code, 200)
        for slug in ('draft', 'future', 'missing'):
            self.assertEqual(self.client.get(reverse('news:detail', args=[slug])).status_code, 404)

    def test_pagination(self):
        for index in range(13):
            article(f'item-{index}', is_published=True)
        first = self.client.get(reverse('news:list'))
        second = self.client.get(reverse('news:list'), {'page': 2})
        self.assertEqual(len(first.data['results']), 12)
        self.assertEqual(len(second.data['results']), 1)
        self.assertIsNotNone(first.data['next'])

    def test_public_api_is_read_only(self):
        response = self.client.post(reverse('news:list'), {'title': 'Не должно сохраниться'})
        self.assertEqual(response.status_code, 405)
        self.assertFalse(NewsArticle.objects.exists())


class NewsAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        credentials = {user_model.USERNAME_FIELD: 'editor@example.com' if user_model.USERNAME_FIELD == 'email' else 'editor'}
        self.user = user_model.objects.create_user(password='password', **credentials)
        self.user.is_staff = True
        self.user.user_permissions.set(Permission.objects.filter(
            content_type__app_label='news', codename__in=(
                'view_newsarticle', 'add_newsarticle', 'change_newsarticle', 'delete_newsarticle',
                'view_newsblock', 'add_newsblock', 'change_newsblock', 'delete_newsblock',
                'view_newscategory', 'add_newscategory', 'change_newscategory', 'delete_newscategory',
            )
        ))
        self.user.save()
        self.client.force_login(self.user)

    def test_editor_can_publish_and_unpublish_without_other_model_access(self):
        add_url = reverse('admin:news_newsarticle_add')
        self.assertEqual(self.client.get(add_url).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:auth_group_changelist')).status_code, 403)
        data = {
            'title': 'Новая статья', 'slug': 'new-story', 'excerpt': 'Анонс',
            'category': '', 'blocks-TOTAL_FORMS': '1', 'blocks-INITIAL_FORMS': '0',
            'blocks-MIN_NUM_FORMS': '0', 'blocks-MAX_NUM_FORMS': '1000',
            'blocks-0-position': '1', 'blocks-0-kind': 'paragraph', 'blocks-0-text': 'Полный текст',
            'published_at_0': (timezone.localdate() - timedelta(days=1)).isoformat(),
            'published_at_1': '10:00:00', 'is_published': 'on',
        }
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 302)
        item = NewsArticle.objects.get(slug='new-story')
        self.assertEqual(self.client.get(reverse('news:list')).data['count'], 1)
        data.pop('is_published')
        data['blocks-TOTAL_FORMS'] = '1'
        data['blocks-INITIAL_FORMS'] = '1'
        data['blocks-0-id'] = str(item.blocks.get().pk)
        data['blocks-0-article'] = str(item.pk)
        data['blocks-0-text'] = 'Исправленный текст'
        response = self.client.post(reverse('admin:news_newsarticle_change', args=[item.pk]), data)
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.blocks.get().text, 'Исправленный текст')
        self.assertFalse(item.is_published)
        self.assertEqual(self.client.get(reverse('news:list')).data['count'], 0)

    def test_admin_rejects_duplicate_slug_and_missing_body(self):
        article('same-slug')
        add_url = reverse('admin:news_newsarticle_add')
        data = {
            'title': 'Другая новость', 'slug': 'same-slug', 'excerpt': 'Анонс',
            'published_at_0': '2026-01-01',
            'published_at_1': '10:00:00',
        }
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('slug', response.context['adminform'].form.errors)
        self.assertEqual(NewsArticle.objects.count(), 1)

        data['slug'] = 'new-slug'
        data['excerpt'] = ''
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('excerpt', response.context['adminform'].form.errors)
        self.assertEqual(NewsArticle.objects.count(), 1)

    def test_view_only_editor_cannot_add_or_change(self):
        item = article('read-only')
        self.user.user_permissions.set(Permission.objects.filter(
            content_type__app_label='news', codename='view_newsarticle'
        ))
        self.assertEqual(self.client.get(reverse('admin:news_newsarticle_add')).status_code, 403)
        change_url = reverse('admin:news_newsarticle_change', args=[item.pk])
        self.assertEqual(self.client.get(change_url).status_code, 200)
        self.assertEqual(self.client.post(change_url, {'title': 'Changed'}).status_code, 403)
        item.refresh_from_db()
        self.assertEqual(item.title, 'read-only')

    def test_editor_can_manage_category_and_blocks(self):
        category_url = reverse('admin:news_newscategory_add')
        response = self.client.post(category_url, {'name': 'Маршруты', 'slug': 'routes'})
        self.assertEqual(response.status_code, 302)
        category = NewsCategory.objects.get(slug='routes')
        item = article('route', category=category)
        self.assertEqual(self.client.get(reverse('admin:news_newsarticle_change', args=[item.pk])).status_code, 200)

    def test_admin_rejects_invalid_inline_block(self):
        response = self.client.post(reverse('admin:news_newsarticle_add'), {
            'title': 'Статья', 'slug': 'inline-test', 'excerpt': 'Анонс',
            'published_at_0': '2026-01-01', 'published_at_1': '10:00:00',
            'blocks-TOTAL_FORMS': '1', 'blocks-INITIAL_FORMS': '0',
            'blocks-MIN_NUM_FORMS': '1', 'blocks-MAX_NUM_FORMS': '1000',
            'blocks-0-position': '1', 'blocks-0-kind': 'image',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NewsArticle.objects.filter(slug='inline-test').exists())
        self.assertTrue(response.context['inline_admin_formsets'][0].formset.errors)


class NewsContentTests(APITestCase):
    def test_category_filter_and_ordered_detail_blocks(self):
        routes = NewsCategory.objects.create(name='Маршруты', slug='routes')
        other = NewsCategory.objects.create(name='События', slug='events')
        item = article('route-story', category=routes, is_published=True)
        article('other-story', category=other, is_published=True)
        NewsBlock.objects.create(article=item, position=2, kind='paragraph', text='Абзац')
        NewsBlock.objects.create(article=item, position=1, kind='heading', text='Подзаголовок')
        response = self.client.get(reverse('news:list'), {'category': 'routes'})
        self.assertEqual([row['slug'] for row in response.data['results']], ['route-story'])
        self.assertEqual(response.data['results'][0]['category']['name'], 'Маршруты')
        detail = self.client.get(reverse('news:detail', args=['route-story']))
        self.assertEqual([block['kind'] for block in detail.data['blocks']], ['heading', 'paragraph'])
        self.assertEqual(len(self.client.get(reverse('news:categories')).data), 2)

    def test_block_validation_requires_fields_for_its_type(self):
        item = article('validations')
        with self.assertRaises(ValidationError):
            NewsBlock(article=item, kind='heading').full_clean()
        with self.assertRaises(ValidationError):
            NewsBlock(article=item, kind='image', alt='Фото').full_clean()
        with self.assertRaises(ValidationError):
            NewsBlock(article=item, kind='paragraph', text='Текст', image=SimpleUploadedFile('a.png', b'not-a-real-image')).full_clean()

    def test_gallery_image_is_in_detail_and_draft_category_is_hidden(self):
        category = NewsCategory.objects.create(name='Путешествия', slug='travel')
        published = article('with-image', category=category, is_published=True)
        NewsBlock.objects.create(article=published, position=1, kind='image', image='news/blocks/photo.jpg', alt='Река', caption='На берегу')
        article('draft-in-category', category=NewsCategory.objects.create(name='Черновики', slug='drafts'))
        detail = self.client.get(reverse('news:detail', args=['with-image']))
        self.assertEqual(detail.data['blocks'][0]['alt'], 'Река')
        self.assertIn('photo.jpg', detail.data['blocks'][0]['image'])
        self.assertEqual([row['slug'] for row in self.client.get(reverse('news:categories')).data], ['travel'])
