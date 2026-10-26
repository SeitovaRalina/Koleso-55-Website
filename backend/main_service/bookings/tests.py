from datetime import date, time, timedelta
from unittest.mock import patch

from rest_framework.test import APITestCase

from accounts.models import CustomUser
from excursions.models import Category, Excursion, Slot
from .models import OrderStatus, TourOrder


class GuestRequestTests(APITestCase):
    def setUp(self):
        category = Category.objects.create(name='Тестовые экскурсии')
        self.excursion = Excursion.objects.create(
            title='Маршрут А', category=category, description='Описание',
            short_description='Краткое описание', price=1000, duration=60, slug='route-a',
        )
        self.other_excursion = Excursion.objects.create(
            title='Маршрут Б', category=category, description='Описание',
            short_description='Краткое описание', price=1500, duration=60, slug='route-b',
        )
        self.slot = Slot.objects.create(
            excursion=self.excursion, date=date.today() + timedelta(days=10),
            time=time(12, 0), max_participants=5,
        )
        self.payload = {
            'excursion': self.excursion.pk, 'slot': self.slot.pk,
            'first_name': 'Иван', 'last_name': 'Иванов',
            'phone': '+79990000000', 'num_participants': 2,
            'contact_method': 'call',
        }

    @patch('bookings.views.publish_recommendation_event')
    def test_guest_request_records_new_order_without_reserving_seats(self, publish):
        response = self.client.post('/api/bookings/orders/', self.payload, format='json')

        self.assertEqual(response.status_code, 201)
        order = TourOrder.objects.get(pk=response.data['id'])
        self.assertIsNone(order.user)
        self.assertEqual(order.status, OrderStatus.NEW)
        self.assertEqual(order.phone, self.payload['phone'])
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.booked_participants, 0)
        publish.assert_called_once()

    def test_request_requires_phone(self):
        response = self.client.post(
            '/api/bookings/orders/', {**self.payload, 'phone': '   '}, format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)
        self.assertFalse(TourOrder.objects.exists())

    def test_request_rejects_slot_from_other_excursion(self):
        response = self.client.post(
            '/api/bookings/orders/',
            {**self.payload, 'excursion': self.other_excursion.pk}, format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('slot', response.data)
        self.assertFalse(TourOrder.objects.exists())

    def test_request_rejects_more_than_available_seats(self):
        response = self.client.post(
            '/api/bookings/orders/',
            {**self.payload, 'num_participants': 6}, format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('slot', response.data)
        self.assertFalse(TourOrder.objects.exists())

    @patch('bookings.views.publish_recommendation_event')
    def test_cancelling_new_request_does_not_release_another_orders_seats(self, publish):
        user = CustomUser.objects.create_user(email='customer@example.com', password='test-password')
        self.client.force_authenticate(user=user)
        self.slot.booked_participants = 2
        self.slot.save(update_fields=['booked_participants'])

        created = self.client.post('/api/bookings/orders/', self.payload, format='json')
        self.assertEqual(created.status_code, 201)
        cancelled = self.client.post(
            f"/api/bookings/my-orders/{created.data['id']}/cancel/", format='json',
        )

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(TourOrder.objects.get(pk=created.data['id']).status, OrderStatus.CANCELLED)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.booked_participants, 2)

    @patch('bookings.views.publish_recommendation_event')
    def test_unverified_customer_gets_profile_warning_without_voucher_promise(self, publish):
        user = CustomUser.objects.create_user(email='guest@example.com', password='test-password')
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/bookings/orders/', self.payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['warnings'], ['Пожалуйста, подтвердите ваш email в профиле'])
        self.assertEqual(TourOrder.objects.get(pk=response.data['id']).status, OrderStatus.NEW)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.booked_participants, 0)
        publish.assert_called_once()
