from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from excursions.models import Excursion, Category
from .models import ExcursionView

User = get_user_model()


class ExcursionViewModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')
        self.excursion = Excursion.objects.create(
            title='Тестовая экскурсия',
            category=self.category,
            description='Описание',
            short_description='Краткое описание',
            price=1000,
            duration=60
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_excursion_view_creation(self):
        """Тест создания записи о просмотре"""
        view = ExcursionView.objects.create(
            user=self.user,
            excursion=self.excursion,
            session_id='test_session_123',
            source='catalog'
        )
        
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.excursion, self.excursion)
        self.assertEqual(view.session_id, 'test_session_123')
        self.assertEqual(view.source, 'catalog')
        self.assertEqual(view.duration_seconds, 0)
        self.assertFalse(view.processed_for_recommendations)

    def test_excursion_view_str(self):
        """Тест строкового представления"""
        view = ExcursionView.objects.create(
            user=self.user,
            excursion=self.excursion,
            session_id='test_session_123',
            source='catalog'
        )
        
        expected = f"Пользователь {self.user.email} - {self.excursion.title} ({view.started_at})"
        self.assertEqual(str(view), expected)


class AnalyticsAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')
        self.excursion = Excursion.objects.create(
            title='Тестовая экскурсия',
            category=self.category,
            description='Описание',
            short_description='Краткое описание',
            price=1000,
            duration=60
        )

    def test_view_start(self):
        """Тест начала отслеживания просмотра"""
        data = {
            'excursion_id': self.excursion.id,
            'session_id': 'test_session_123',
            'source': 'catalog'
        }
        
        response = self.client.post('/api/analytics/view/start/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('view_id', response.data)
        
        view = ExcursionView.objects.get(id=response.data['view_id'])
        self.assertEqual(view.excursion, self.excursion)
        self.assertEqual(view.session_id, 'test_session_123')
        self.assertEqual(view.source, 'catalog')

    def test_view_start_invalid_excursion(self):
        """Тест начала просмотра с несуществующей экскурсией"""
        data = {
            'excursion_id': 999,
            'session_id': 'test_session_123',
            'source': 'catalog'
        }
        
        response = self.client.post('/api/analytics/view/start/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('analytics.tasks.publish_event.delay')
    def test_view_end_with_long_duration(self, mock_publish):
        """Тест завершения просмотра с длительностью > 5 секунд"""
        view = ExcursionView.objects.create(
            excursion=self.excursion,
            session_id='test_session_123',
            source='catalog',
            duration_seconds=10
        )
        
        data = {'view_id': view.id}
        response = self.client.post('/api/analytics/view/end/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_publish.assert_called_once()
        
        view.refresh_from_db()
        self.assertTrue(view.processed_for_recommendations)

    def test_view_end_with_short_duration(self):
        """Тест завершения просмотра с длительностью <= 5 секунд"""
        view = ExcursionView.objects.create(
            excursion=self.excursion,
            session_id='test_session_123',
            source='catalog',
            duration_seconds=3
        )
        
        data = {'view_id': view.id}
        response = self.client.post('/api/analytics/view/end/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        view.refresh_from_db()
        self.assertFalse(view.processed_for_recommendations)
