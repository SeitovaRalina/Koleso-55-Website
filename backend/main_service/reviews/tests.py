from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from excursions.models import Category, Excursion
from .models import Review, ReviewStatus


class ReviewAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com', password='test-password',
        )
        cls.staff_user = get_user_model().objects.create_user(
            email='staff@example.com', password='test-password', is_staff=True,
        )
        cls.site_user = get_user_model().objects.create_user(
            email='client@example.com', password='test-password',
        )
        category = Category.objects.create(name='Тестовая категория')
        cls.excursion = Excursion.objects.create(
            title='Тестовая экскурсия', category=category,
            description='Описание', short_description='Описание', price=1000, duration=60,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)
        self.add_url = reverse('admin:reviews_review_add')

    def form_data(self, **changes):
        data = {
            'manual_first_name': 'Анна',
            'manual_last_name': 'Иванова',
            'excursion': str(self.excursion.pk),
            'rating': '5',
            'text': 'Отличная экскурсия',
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
        }
        data.update(changes)
        return data

    def test_add_form_creates_pending_review_without_user(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'manual_first_name')
        self.assertNotContains(response, 'name="user"')

        response = self.client.post(self.add_url, self.form_data())
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get()
        self.assertTrue(review.is_admin_added)
        self.assertIsNone(review.user)
        self.assertEqual(review.status, ReviewStatus.PENDING)
        self.assertEqual(review.author_name, 'Иванова Анна')

    def test_missing_fields_are_form_errors_not_server_error(self):
        for changes in ({'manual_first_name': ''}, {'excursion': ''}, {'rating': ''}, {'text': ''}):
            with self.subTest(changes=changes):
                response = self.client.post(self.add_url, self.form_data(**changes))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['adminform'].form.errors)
        self.assertFalse(Review.objects.exists())

    def test_edit_and_exact_duplicate(self):
        self.client.post(self.add_url, self.form_data())
        review = Review.objects.get()
        duplicate = self.client.post(self.add_url, self.form_data())
        self.assertEqual(duplicate.status_code, 200)
        self.assertContains(duplicate, 'Такой ручной отзыв уже существует')
        self.assertEqual(Review.objects.count(), 1)

        change_url = reverse('admin:reviews_review_change', args=[review.pk])
        data = self.form_data(text='Обновлённый текст', status=ReviewStatus.APPROVED,
                              show_on_homepage='on', homepage_order='100',
                              homepage_author_name='', moderator_comment='')
        response = self.client.post(change_url, data)
        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.text, 'Обновлённый текст')
        self.assertEqual(review.status, ReviewStatus.APPROVED)
        self.assertIsNone(review.user)

    def test_staff_without_review_permissions_cannot_add_or_edit(self):
        review = Review.objects.create(
            excursion=self.excursion, is_admin_added=True,
            manual_first_name='Анна', manual_last_name='Иванова',
            rating=5, text='Отзыв',
        )
        self.client.force_login(self.staff_user)
        self.assertEqual(self.client.get(self.add_url).status_code, 403)
        self.assertEqual(self.client.post(self.add_url, self.form_data()).status_code, 403)
        change_url = reverse('admin:reviews_review_change', args=[review.pk])
        self.assertEqual(self.client.get(change_url).status_code, 403)

    def test_online_review_keeps_user_uniqueness_and_api_identity(self):
        Review.objects.create(
            user=self.site_user, excursion=self.excursion, rating=4, text='С сайта',
            status=ReviewStatus.APPROVED,
        )
        manual = Review.objects.create(
            excursion=self.excursion, is_admin_added=True,
            manual_first_name='Анна', manual_last_name='Иванова',
            rating=5, text='Вне сайта', status=ReviewStatus.APPROVED,
        )
        response = self.client.get(reverse('review-list', args=[self.excursion.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Иванова Анна', str(response.data))
        self.client.force_login(self.site_user)
        my_reviews = self.client.get(reverse('my-reviews'))
        self.assertEqual(my_reviews.status_code, 200)
        self.assertNotIn(manual.pk, [item['id'] for item in my_reviews.data['results']])
