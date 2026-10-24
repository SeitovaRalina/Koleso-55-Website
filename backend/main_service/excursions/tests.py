import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Excursion, ExcursionInquiry


class ExcursionInquiryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        category = Category.objects.create(name='Город', slug='city')
        self.excursion = Excursion.objects.create(
            title='Программа', slug='program', category=category,
            description='Описание', short_description='Кратко', price=1000, duration=60,
        )
        self.payload = {
            'request_id': str(uuid.uuid4()), 'excursion': self.excursion.pk,
            'name': 'Иван', 'phone': '+7 (999) 123-45-67',
            'contact_method': 'telegram', 'question': 'Где встречаемся?',
        }

    def test_guest_creates_inquiry_and_admin_can_process_it(self):
        response = self.client.post('/api/excursions/inquiries/', self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        inquiry = ExcursionInquiry.objects.get(pk=response.data['id'])
        self.assertEqual(inquiry.excursion, self.excursion)
        self.assertEqual(inquiry.phone, self.payload['phone'])
        self.assertEqual(inquiry.status, 'new')
        self.assertIsNotNone(inquiry.created_at)
        admin = get_user_model().objects.create_superuser('admin@example.com', 'password')
        self.client.force_login(admin)
        page = self.client.get('/admin/excursions/excursioninquiry/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Программа')
        change = self.client.get(f'/admin/excursions/excursioninquiry/{inquiry.pk}/change/')
        self.assertEqual(change.status_code, 200)
        self.assertContains(change, 'Где встречаемся?')
        update = self.client.post(
            f'/admin/excursions/excursioninquiry/{inquiry.pk}/change/',
            {'status': 'in_progress', '_save': 'Save'},
        )
        self.assertEqual(update.status_code, 302)
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'in_progress')

    def test_duplicate_key_is_idempotent_and_conflict_is_rejected(self):
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 201)
        self.assertEqual(ExcursionInquiry.objects.count(), 1)
        changed = {**self.payload, 'question': 'Другой вопрос'}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', changed, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 1)

    def test_invalid_input_and_unknown_or_inactive_program_are_rejected(self):
        self.assertEqual(self.client.get('/api/excursions/inquiries/').status_code, 405)
        invalid = {**self.payload, 'phone': '123', 'question': 'x'}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', invalid, format='json').status_code, 400)
        unknown = {**self.payload, 'excursion': 999999}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', unknown, format='json').status_code, 400)
        self.excursion.is_active = False
        self.excursion.save()
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 0)

    def test_rate_limit(self):
        for _ in range(5):
            payload = {**self.payload, 'request_id': str(uuid.uuid4())}
            self.assertEqual(self.client.post('/api/excursions/inquiries/', payload, format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', {**self.payload, 'request_id': str(uuid.uuid4())}, format='json').status_code, 429)
        self.assertEqual(ExcursionInquiry.objects.count(), 5)
