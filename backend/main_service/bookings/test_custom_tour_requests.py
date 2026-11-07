from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import CustomTourRequest


class CustomTourRequestApiTests(APITestCase):
    payload = {
        'name': 'Ирина Руснак',
        'phone': '+7 900 000-00-00',
        'email': 'irina@example.test',
        'description': 'Нужна программа для школьной группы в июне.',
    }

    def test_guest_can_create_request(self):
        response = self.client.post(reverse('bookings:custom-tour-request-create'), self.payload)

        self.assertEqual(response.status_code, 201)
        request = CustomTourRequest.objects.get(pk=response.data['id'])
        self.assertIsNone(request.user)
        self.assertEqual(request.status, CustomTourRequest.Status.NEW)

    def test_authenticated_user_sees_only_own_requests(self):
        user = get_user_model().objects.create_user(email='customer@example.test', password='test-password')
        other_user = get_user_model().objects.create_user(email='other@example.test', password='test-password')
        own_request = CustomTourRequest.objects.create(user=user, **self.payload)
        CustomTourRequest.objects.create(user=other_user, **{**self.payload, 'email': 'other@example.test'})

        self.client.force_authenticate(user)
        response = self.client.get(reverse('bookings:my-custom-tour-request-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['results']], [own_request.id])
