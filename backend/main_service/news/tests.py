from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import NewsArticle


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
        self.assertEqual(response.data['results'][0]['body'], 'Полный текст')

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


class NewsAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        credentials = {user_model.USERNAME_FIELD: 'editor@example.com' if user_model.USERNAME_FIELD == 'email' else 'editor'}
        self.user = user_model.objects.create_user(password='password', **credentials)
        self.user.is_staff = True
        self.user.user_permissions.set(Permission.objects.filter(
            content_type__app_label='news', codename__in=(
                'view_newsarticle', 'add_newsarticle', 'change_newsarticle', 'delete_newsarticle'
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
            'body': 'Полный текст', 'category': 'Новости',
            'published_at_0': (timezone.localdate() - timedelta(days=1)).isoformat(),
            'published_at_1': '10:00:00', 'is_published': 'on',
        }
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 302)
        item = NewsArticle.objects.get(slug='new-story')
        self.assertEqual(self.client.get(reverse('news:list')).data['count'], 1)
        data.pop('is_published')
        response = self.client.post(reverse('admin:news_newsarticle_change', args=[item.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get(reverse('news:list')).data['count'], 0)
