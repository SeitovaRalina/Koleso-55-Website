from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .admin import GiftCertificateRequestAdmin
from .models import GiftCertificateRequest


class GiftCertificateRequestAPITests(APITestCase):
    url = reverse('bookings:certificate-request-create')
    payload = {
        'buyer_name': 'Покупатель',
        'buyer_phone': '+79000000000',
        'buyer_email': 'buyer@example.com',
        'recipient_name': 'Получатель',
        'recipient_phone': '',
        'recipient_email': '',
        'amount': 3000,
        'format': 'digital',
        'message': 'Поздравляем!',
    }

    def test_guest_request_is_saved_with_new_status(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        request = GiftCertificateRequest.objects.get(pk=response.data['id'])
        self.assertEqual(request.buyer_email, self.payload['buyer_email'])
        self.assertEqual(request.recipient_name, self.payload['recipient_name'])
        self.assertEqual(request.amount, 3000)
        self.assertEqual(request.format, 'digital')
        self.assertEqual(request.status, GiftCertificateRequest.Status.NEW)
        self.assertNotIn('status', response.data)

    def test_invalid_fields_do_not_create_request(self):
        for field, value in [('amount', 1234), ('format', 'unknown'), ('buyer_email', 'bad'), ('buyer_name', '   ')]:
            with self.subTest(field=field):
                payload = {**self.payload, field: value}
                response = self.client.post(self.url, payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(GiftCertificateRequest.objects.count(), 0)

    def test_public_list_is_not_available(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_client_cannot_set_processing_status(self):
        response = self.client.post(self.url, {**self.payload, 'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(GiftCertificateRequest.objects.get(pk=response.data['id']).status, 'new')

    def test_repeat_submission_creates_separate_requests(self):
        first = self.client.post(self.url, self.payload, format='json')
        second = self.client.post(self.url, self.payload, format='json')
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertNotEqual(first.data['id'], second.data['id'])
        self.assertEqual(GiftCertificateRequest.objects.count(), 2)


class GiftCertificateRequestAdminTests(TestCase):
    def test_admin_requires_staff_and_model_permissions(self):
        url = reverse('admin:bookings_giftcertificaterequest_changelist')
        self.assertEqual(self.client.get(url).status_code, 302)
        user = get_user_model().objects.create_user(email='guest@example.com', password='test-password')
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 302)
        user.is_staff = True
        user.save(update_fields=['is_staff'])
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_admin_lists_contact_details_and_can_change_status(self):
        model_admin = admin.site._registry[GiftCertificateRequest]
        self.assertIsInstance(model_admin, GiftCertificateRequestAdmin)
        self.assertIn('status', model_admin.list_display)
        self.assertIn('buyer_email', model_admin.readonly_fields)
        self.assertIn('recipient_name', model_admin.list_display)

        request = GiftCertificateRequest.objects.create(
            buyer_name='Покупатель', buyer_phone='+79000000000', buyer_email='buyer@example.com',
            recipient_name='Получатель', amount=5000, format='printed',
        )
        user = get_user_model().objects.create_superuser(email='admin@example.com', password='test-password')
        self.client.force_login(user)
        url = reverse('admin:bookings_giftcertificaterequest_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'Покупатель')
        self.assertContains(response, 'Получатель')
        self.assertContains(response, '5000')

        change_url = reverse('admin:bookings_giftcertificaterequest_change', args=[request.pk])
        response = self.client.post(change_url, {'status': GiftCertificateRequest.Status.IN_PROGRESS, '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.status, GiftCertificateRequest.Status.IN_PROGRESS)

        response = self.client.post(change_url, {'status': GiftCertificateRequest.Status.COMPLETED, '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.status, GiftCertificateRequest.Status.COMPLETED)

        response = self.client.post(change_url, {'status': 'invalid', '_save': 'Save'})
        self.assertEqual(response.status_code, 200)
        request.refresh_from_db()
        self.assertEqual(request.status, GiftCertificateRequest.Status.COMPLETED)
